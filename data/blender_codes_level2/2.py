import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 12.0
bridge_height = 2.5
chord_length = 1.0
chord_cross_section = (0.2, 0.2)
diagonal_length_given = 1.118
diagonal_cross_section = (0.15, 0.15)
vertical_length = 2.5
vertical_cross_section = (0.15, 0.15)
support_radius = 0.3
support_height = 0.5
num_nodes = 13
node_positions_x = [-6.0 + i * chord_length for i in range(num_nodes)]
load_block_size = 0.5
load_block_mass = 600
load_block_position = (0.0, 0.0, 2.5)
gravity = -9.81

# Create a collection for bridge parts
bridge_collection = bpy.data.collections.new("Bridge")
bpy.context.scene.collection.children.link(bridge_collection)

# Function to create a member between two points
def create_member(name, start, end, cross_section, length_scale=1.0):
    # Calculate midpoint and direction vector
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    # Scale: cross-section in X/Y, length in Z (cube default size 2, so divide by 2)
    obj.scale = (cross_section[0]/2, cross_section[1]/2, length/2 * length_scale)
    
    # Rotate to align with vector
    if length > 0:
        # Calculate rotation quaternion from Z-axis to vector
        axis = (dy, -dx, 0)  # perpendicular to Z and vector
        axis_len = math.sqrt(axis[0]*axis[0] + axis[1]*axis[1] + axis[2]*axis[2])
        if axis_len > 0:
            axis = (axis[0]/axis_len, axis[1]/axis_len, axis[2]/axis_len)
            angle = math.acos(dz / length)
            obj.rotation_mode = 'AXIS_ANGLE'
            obj.rotation_axis_angle = (angle, axis[0], axis[1], axis[2])
    
    # Move to bridge collection
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    bridge_collection.objects.link(obj)
    return obj

# Create top chord (13 members)
top_nodes = [(x, 0.0, bridge_height) for x in node_positions_x]
for i in range(num_nodes - 1):
    create_member(f"TopChord_{i}", top_nodes[i], top_nodes[i+1], chord_cross_section)

# Create bottom chord (13 members)
bottom_nodes = [(x, 0.0, 0.0) for x in node_positions_x]
for i in range(num_nodes - 1):
    create_member(f"BottomChord_{i}", bottom_nodes[i], bottom_nodes[i+1], chord_cross_section)

# Create vertical members (11 members, skip ends)
for i in range(1, num_nodes - 1):
    start = bottom_nodes[i]
    end = top_nodes[i]
    create_member(f"Vertical_{i}", start, end, vertical_cross_section)

# Create diagonal members (12 members, alternating pattern)
# Diagonal connects top node i to bottom node i+1 for even i, bottom node i to top node i+1 for odd i
for i in range(num_nodes - 1):
    if i % 2 == 0:
        start = top_nodes[i]
        end = bottom_nodes[i+1]
    else:
        start = bottom_nodes[i]
        end = top_nodes[i+1]
    # Compute actual length and scaling factor
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    actual_length = math.sqrt(dx*dx + dz*dz)
    scale_factor = actual_length / diagonal_length_given
    create_member(f"Diagonal_{i}", start, end, diagonal_cross_section, length_scale=scale_factor)

# Create support columns (cylinders at ends)
for i, x in enumerate([-6.0, 6.0]):
    bpy.ops.mesh.primitive_cylinder_add(radius=support_radius, depth=support_height, location=(x, 0.0, support_height/2))
    support = bpy.context.active_object
    support.name = f"Support_{i}"
    if support.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(support)
    bridge_collection.objects.link(support)

# Join all bridge parts into a single object
bpy.ops.object.select_all(action='DESELECT')
for obj in bridge_collection.objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = bridge_collection.objects[0]
bpy.ops.object.join()
bridge = bpy.context.active_object
bridge.name = "WarrenBridge"

# Add rigid body to bridge (passive)
bpy.ops.rigidbody.object_add()
bridge.rigid_body.type = 'PASSIVE'
bridge.rigid_body.collision_shape = 'MESH'

# Create load block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_block_position)
load_block = bpy.context.active_object
load_block.name = "LoadBlock"
load_block.scale = (load_block_size, load_block_size, load_block_size)
bpy.ops.rigidbody.object_add()
load_block.rigid_body.type = 'ACTIVE'
load_block.rigid_body.mass = load_block_mass
load_block.rigid_body.collision_shape = 'BOX'

# Add fixed constraint between load block and bridge
bpy.ops.object.select_all(action='DESELECT')
bridge.select_set(True)
load_block.select_set(True)
bpy.context.view_layer.objects.active = load_block
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Fixed_Constraint"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = bridge
constraint.rigid_body_constraint.object2 = load_block

# Set world gravity
bpy.context.scene.gravity = (0.0, 0.0, gravity)

# Ensure all objects are in scene collection
for obj in [bridge, load_block, constraint]:
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)