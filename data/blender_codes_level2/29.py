import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
L = 10.0
H = 2.0
panels = 5
panel_w = 2.0
top_section = (0.2, 0.2)
bot_section = (0.2, 0.2)
diag_section = (0.15, 0.15)
diag_angle = 60.0
diag_len = 2.3094
top_x = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
top_z = 2.0
bot_x = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
bot_z = 0.0
load_x = [2.5, 5.0, 7.5]
load_z = 0.1
total_force = 11772.0
force_per = 3924.0

# Node dictionary to store objects for constraint creation
nodes = {}

# Create top chord (6 segments)
for i in range(len(top_x)-1):
    # Calculate segment center and length
    x1, x2 = top_x[i], top_x[i+1]
    x_center = (x1 + x2) / 2
    length = abs(x2 - x1)
    
    # Create cube and scale to segment dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_center, 0, top_z))
    chord = bpy.context.active_object
    chord.name = f"top_chord_{i}"
    chord.scale = (length/2, top_section[0]/2, top_section[1]/2)
    
    # Add rigid body (passive)
    bpy.ops.rigidbody.object_add()
    chord.rigid_body.type = 'PASSIVE'
    chord.rigid_body.collision_shape = 'BOX'
    
    # Store nodes for constraint creation
    node1_key = f"node_{x1}_{top_z}"
    node2_key = f"node_{x2}_{top_z}"
    
    if node1_key not in nodes:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x1, 0, top_z))
        nodes[node1_key] = bpy.context.active_object
    if node2_key not in nodes:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x2, 0, top_z))
        nodes[node2_key] = bpy.context.active_object

# Create bottom chord (5 segments)
for i in range(len(bot_x)-1):
    x1, x2 = bot_x[i], bot_x[i+1]
    x_center = (x1 + x2) / 2
    length = abs(x2 - x1)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_center, 0, bot_z))
    chord = bpy.context.active_object
    chord.name = f"bottom_chord_{i}"
    chord.scale = (length/2, bot_section[0]/2, bot_section[1]/2)
    
    bpy.ops.rigidbody.object_add()
    chord.rigid_body.type = 'PASSIVE'
    chord.rigid_body.collision_shape = 'BOX'
    
    # Store bottom nodes
    node1_key = f"node_{x1}_{bot_z}"
    node2_key = f"node_{x2}_{bot_z}"
    
    if node1_key not in nodes:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x1, 0, bot_z))
        nodes[node1_key] = bpy.context.active_object
    if node2_key not in nodes:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x2, 0, bot_z))
        nodes[node2_key] = bpy.context.active_object

# Create diagonal members (alternating pattern)
for i in range(panels):
    if i % 2 == 0:  # Upward diagonals
        start_x, start_z = bot_x[i], bot_z
        end_x, end_z = top_x[i+1], top_z
    else:  # Downward diagonals
        start_x, start_z = top_x[i], top_z
        end_x, end_z = bot_x[i+1], bot_z
    
    # Calculate center and rotation
    center_x = (start_x + end_x) / 2
    center_z = (start_z + end_z) / 2
    dx = end_x - start_x
    dz = end_z - start_z
    angle = math.atan2(dz, dx)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, 0, center_z))
    diag = bpy.context.active_object
    diag.name = f"diagonal_{i}"
    diag.scale = (diag_len/2, diag_section[0]/2, diag_section[1]/2)
    diag.rotation_euler = (0, angle, 0)
    
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'PASSIVE'
    diag.rigid_body.collision_shape = 'BOX'

# Create fixed constraints at all nodes
for node_key, node_obj in nodes.items():
    # Find all members connected to this node
    x, z = node_obj.location.x, node_obj.location.z
    connected_objects = []
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith(('top_chord', 'bottom_chord', 'diagonal')):
            # Check if object bounds contain the node
            bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            bbox_x = [v.x for v in bbox]
            bbox_z = [v.z for v in bbox]
            
            if min(bbox_x) <= x <= max(bbox_x) and min(bbox_z) <= z <= max(bbox_z):
                connected_objects.append(obj)
    
    # Create fixed constraints between node and each connected member
    for member in connected_objects:
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"constraint_{node_key}_{member.name}"
        constraint.rigid_body_constraint.object1 = node_obj
        constraint.rigid_body_constraint.object2 = member

# Create load application points
load_objects = []
for i, lx in enumerate(load_x):
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(lx, 0, load_z))
    load = bpy.context.active_object
    load.name = f"load_point_{i}"
    load.scale = (0.05, 0.05, 0.05)
    
    bpy.ops.rigidbody.object_add()
    load.rigid_body.type = 'ACTIVE'
    load.rigid_body.mass = 400.0  # Mass corresponding to 3924N force at 9.81m/s²
    load.rigid_body.collision_shape = 'BOX'
    load_objects.append(load)
    
    # Find nearest bottom chord nodes for constraint
    nearest_nodes = []
    for node_key in nodes:
        if f"_{bot_z}" in node_key:  # Bottom chord nodes
            node_x = float(node_key.split('_')[1])
            if abs(node_x - lx) <= panel_w/2:
                nearest_nodes.append(nodes[node_key])
    
    # Connect load point to nearest nodes
    for node in nearest_nodes[:2]:  # Connect to up to 2 nearest nodes
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"load_constraint_{i}_{node.name}"
        constraint.rigid_body_constraint.object1 = load
        constraint.rigid_body_constraint.object2 = node

# Setup rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Apply forces to load points (downward)
for load in load_objects:
    load.rigid_body.force = (0, 0, -force_per)

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

print("Warren Truss construction complete. Simulation ready.")
print(f"Total force applied: {total_force} N")
print(f"Force per load point: {force_per} N")
print(f"Maximum allowed displacement: {0.05} m")