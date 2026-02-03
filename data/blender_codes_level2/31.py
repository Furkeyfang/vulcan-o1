import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
span_length = 9.0
bridge_width = 1.0
bridge_height = 2.0
cube_size = 0.2
num_bays = 9
num_joints = num_bays + 1
joint_spacing = span_length / num_bays
vertical_scale_z = bridge_height / cube_size
horizontal_scale_x = joint_spacing / cube_size
diagonal_scale_x = math.sqrt(joint_spacing**2 + bridge_height**2) / cube_size
y_scale = bridge_width / cube_size

load_mass = 600.0
load_size = (1.0, 1.0, 0.5)
load_pos = (4.5, 0.0, 2.5)

# Create bottom chord (horizontal members along X at Z=0)
bottom_members = []
for i in range(num_bays):
    x_pos = i * joint_spacing + joint_spacing/2
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(x_pos, 0, 0))
    member = bpy.context.active_object
    member.scale = (horizontal_scale_x, y_scale, 1.0)
    member.name = f"bottom_chord_{i}"
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'PASSIVE'
    bottom_members.append(member)

# Create top chord (horizontal members along X at Z=bridge_height)
top_members = []
for i in range(num_bays):
    x_pos = i * joint_spacing + joint_spacing/2
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(x_pos, 0, bridge_height))
    member = bpy.context.active_object
    member.scale = (horizontal_scale_x, y_scale, 1.0)
    member.name = f"top_chord_{i}"
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'PASSIVE'
    top_members.append(member)

# Create vertical members
vertical_members = []
for i in range(num_joints):
    x_pos = i * joint_spacing
    z_pos = bridge_height / 2
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(x_pos, 0, z_pos))
    member = bpy.context.active_object
    member.scale = (1.0, y_scale, vertical_scale_z)
    member.name = f"vertical_{i}"
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'PASSIVE'
    vertical_members.append(member)

# Create diagonal members (alternating pattern)
diagonal_members = []
for i in range(num_bays):
    # Start and end points
    if i % 2 == 0:  # Bottom-left to top-right
        start_pos = (i * joint_spacing, 0, 0)
        end_pos = ((i+1) * joint_spacing, 0, bridge_height)
    else:  # Top-left to bottom-right
        start_pos = (i * joint_spacing, 0, bridge_height)
        end_pos = ((i+1) * joint_spacing, 0, 0)
    
    # Midpoint and rotation
    mid_x = (start_pos[0] + end_pos[0]) / 2
    mid_z = (start_pos[2] + end_pos[2]) / 2
    dx = end_pos[0] - start_pos[0]
    dz = end_pos[2] - start_pos[2]
    angle = math.atan2(dz, dx)
    
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(mid_x, 0, mid_z))
    member = bpy.context.active_object
    member.scale = (diagonal_scale_x, y_scale, 1.0)
    member.rotation_euler = (0, angle, 0)
    member.name = f"diagonal_{i}"
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'PASSIVE'
    diagonal_members.append(member)

# Create fixed constraints between connected members
def add_fixed_constraint(obj1, obj2):
    # Select obj1 then obj2
    bpy.context.view_layer.objects.active = obj1
    obj1.select_set(True)
    obj2.select_set(True)
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Connect verticals to bottom chord
for i, vert in enumerate(vertical_members):
    # Connect to left bottom member (if exists)
    if i > 0:
        add_fixed_constraint(vert, bottom_members[i-1])
    # Connect to right bottom member (if exists)
    if i < num_bays:
        add_fixed_constraint(vert, bottom_members[i])

# Connect verticals to top chord
for i, vert in enumerate(vertical_members):
    # Connect to left top member (if exists)
    if i > 0:
        add_fixed_constraint(vert, top_members[i-1])
    # Connect to right top member (if exists)
    if i < num_bays:
        add_fixed_constraint(vert, top_members[i])

# Connect diagonals to chords
for i, diag in enumerate(diagonal_members):
    if i % 2 == 0:  # Bottom-left to top-right
        add_fixed_constraint(diag, bottom_members[i])
        add_fixed_constraint(diag, top_members[i])
    else:  # Top-left to bottom-right
        add_fixed_constraint(diag, top_members[i])
        add_fixed_constraint(diag, bottom_members[i])

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos)
load_cube = bpy.context.active_object
load_cube.scale = load_size
load_cube.name = "load_600kg"
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass

# Attach load to nearest top chord member (center bay)
center_bay_index = num_bays // 2
add_fixed_constraint(load_cube, top_members[center_bay_index])

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Ensure all objects are properly selected/deselected for clean state
bpy.ops.object.select_all(action='DESELECT')