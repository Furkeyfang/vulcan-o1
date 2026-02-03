import bpy
import math
from mathutils import Vector

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
total_span = 15.0
truss_height_center = 2.5
truss_height_end = 0.5
num_panels = 6
panel_width = total_span / num_panels
bottom_chord_cross_section = 0.2
top_chord_cross_section = 0.2
web_cross_section = 0.15
support_loc_left = (-7.5, 0, 0)
support_loc_right = (7.5, 0, 0)
support_size = (0.5, 0.5, 0.5)
total_force = 19620.0
force_per_node = total_force / 7  # 7 top nodes

# Calculate node positions
bottom_nodes = []
top_nodes = []
for i in range(num_panels + 1):
    x = -total_span/2 + i * panel_width
    bottom_nodes.append(Vector((x, 0, 0)))
    
    # Top chord Z-coordinate (linear slope from ends to center)
    if x <= 0:
        z_top = truss_height_end + (truss_height_center - truss_height_end) * (x + total_span/2) / (total_span/2)
    else:
        z_top = truss_height_center - (truss_height_center - truss_height_end) * x / (total_span/2)
    top_nodes.append(Vector((x, 0, z_top)))

# Function to create truss member between two points
def create_member(start, end, cross_section, name):
    # Calculate length and direction
    vec = end - start
    length = vec.length
    center = (start + end) / 2
    
    # Create cube and scale to member dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    member = bpy.context.active_object
    member.name = name
    
    # Rotate to align with member direction
    if length > 0:
        up = Vector((0, 0, 1))
        rot_quat = up.rotation_difference(vec)
        member.rotation_euler = rot_quat.to_euler()
    
    # Scale: cross-section in Y/Z, length in X
    member.scale = (length/2, cross_section/2, cross_section/2)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    member.rigid_body.mass = length * cross_section * cross_section * 7850  # Steel density kg/m³
    
    return member

# Create bottom chord
bottom_members = []
for i in range(num_panels):
    member = create_member(
        bottom_nodes[i], 
        bottom_nodes[i+1], 
        bottom_chord_cross_section, 
        f"bottom_chord_{i}"
    )
    bottom_members.append(member)

# Create top chord
top_members = []
for i in range(num_panels):
    member = create_member(
        top_nodes[i], 
        top_nodes[i+1], 
        top_chord_cross_section, 
        f"top_chord_{i}"
    )
    top_members.append(member)
    
    # Apply distributed load (tributary area method)
    if i == 0 or i == num_panels-1:
        # End members: half panel load + half adjacent
        force_magnitude = 1.5 * force_per_node
    else:
        # Interior members: full panel load from both sides
        force_magnitude = 2.0 * force_per_node
    
    # Apply downward force at center of member
    member.rigid_body.linear_velocity = (0, 0, -force_magnitude / member.rigid_body.mass)

# Create vertical members
vertical_members = []
for i in range(num_panels + 1):
    member = create_member(
        bottom_nodes[i], 
        top_nodes[i], 
        web_cross_section, 
        f"vertical_{i}"
    )
    vertical_members.append(member)

# Create diagonal members (Howe pattern: slope toward center)
diagonal_members = []
for i in range(num_panels):
    if i < num_panels/2:  # Left half
        start = bottom_nodes[i]
        end = top_nodes[i+1]
    else:  # Right half
        start = bottom_nodes[i+1]
        end = top_nodes[i]
    
    member = create_member(start, end, web_cross_section, f"diagonal_{i}")
    diagonal_members.append(member)

# Create support blocks at ends
for loc, name in [(support_loc_left, "support_left"), (support_loc_right, "support_right")]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    support = bpy.context.active_object
    support.name = name
    support.scale = Vector(support_size)
    
    bpy.ops.rigidbody.object_add()
    support.rigid_body.type = 'PASSIVE'
    support.rigid_body.collision_shape = 'BOX'

# Create fixed constraints at all nodes
def create_fixed_constraint(obj1, obj2):
    # Select objects and set active
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.type = 'FIXED'
    
    # Parent constraint to first object
    constraint.location = obj1.location
    
    # Set connected objects
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Connect members at each bottom node
for i in range(num_panels + 1):
    connected_objs = []
    
    # Bottom chord connections
    if i > 0:
        connected_objs.append(bottom_members[i-1])
    if i < num_panels:
        connected_objs.append(bottom_members[i])
    
    # Vertical connection
    connected_objs.append(vertical_members[i])
    
    # Diagonal connections
    if i < num_panels:  # Left diagonal
        for diag in diagonal_members:
            if (diag.name.startswith(f"diagonal_{i}") and i < num_panels/2) or 
               (diag.name.startswith(f"diagonal_{i-1}") and i > 0 and i > num_panels/2):
                connected_objs.append(diag)
                break
    
    # Create constraints between first object and all others
    if len(connected_objs) >= 2:
        for j in range(1, len(connected_objs)):
            create_fixed_constraint(connected_objs[0], connected_objs[j])

# Connect members at each top node
for i in range(num_panels + 1):
    connected_objs = []
    
    # Top chord connections
    if i > 0:
        connected_objs.append(top_members[i-1])
    if i < num_panels:
        connected_objs.append(top_members[i])
    
    # Vertical connection
    connected_objs.append(vertical_members[i])
    
    # Diagonal connections
    if i > 0 and i <= num_panels/2:  # Left diagonals
        for diag in diagonal_members:
            if diag.name.startswith(f"diagonal_{i-1}"):
                connected_objs.append(diag)
                break
    elif i < num_panels and i >= num_panels/2:  # Right diagonals
        for diag in diagonal_members:
            if diag.name.startswith(f"diagonal_{i}"):
                connected_objs.append(diag)
                break
    
    # Create constraints
    if len(connected_objs) >= 2:
        for j in range(1, len(connected_objs)):
            create_fixed_constraint(connected_objs[0], connected_objs[j])

# Connect supports to end verticals
create_fixed_constraint(vertical_members[0], bpy.data.objects["support_left"])
create_fixed_constraint(vertical_members[-1], bpy.data.objects["support_right"])

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

print("Howe truss roof structure created successfully.")