import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define variables from parameter summary
span_length = 18.0
truss_depth = 2.0
top_chord_z = 5.0
bottom_chord_z = 3.0
bay_length = 3.0
num_bays = 6
beam_cross_section = 0.5
vertical_height = 2.0
joint_radius = 0.25
joint_depth = 0.5
diagonal_length = math.sqrt(bay_length**2 + truss_depth**2)
load_mass = 2500.0
load_plate_size = (1.0, 1.0, 0.1)
simulation_frames = 100
max_displacement = 0.1

# Calculate node positions
node_x_positions = [-span_length/2 + i*bay_length for i in range(num_bays + 1)]
top_nodes = [(x, 0, top_chord_z) for x in node_x_positions]
bottom_nodes = [(x, 0, bottom_chord_z) for x in node_x_positions]

# Store created objects for constraint creation
joint_objects = []
beam_objects = []

# Create joint cylinders at all nodes
for i, (top_pos, bottom_pos) in enumerate(zip(top_nodes, bottom_nodes)):
    # Top joint
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=joint_radius,
        depth=joint_depth,
        location=(top_pos[0], top_pos[1], top_pos[2])
    )
    top_joint = bpy.context.active_object
    top_joint.name = f"top_joint_{i}"
    bpy.ops.rigidbody.object_add()
    top_joint.rigid_body.type = 'PASSIVE'
    joint_objects.append(top_joint)
    
    # Bottom joint
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=joint_radius,
        depth=joint_depth,
        location=(bottom_pos[0], bottom_pos[1], bottom_pos[2])
    )
    bottom_joint = bpy.context.active_object
    bottom_joint.name = f"bottom_joint_{i}"
    bpy.ops.rigidbody.object_add()
    bottom_joint.rigid_body.type = 'PASSIVE'
    joint_objects.append(bottom_joint)

# Create top chord segments (6 cubes, each 3m long)
for i in range(num_bays):
    start_x = node_x_positions[i]
    end_x = node_x_positions[i+1]
    mid_x = (start_x + end_x) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid_x, 0, top_chord_z))
    top_segment = bpy.context.active_object
    top_segment.name = f"top_chord_{i}"
    top_segment.scale = (bay_length, beam_cross_section, beam_cross_section)
    bpy.ops.rigidbody.object_add()
    top_segment.rigid_body.type = 'PASSIVE'
    beam_objects.append(top_segment)

# Create bottom chord segments
for i in range(num_bays):
    start_x = node_x_positions[i]
    end_x = node_x_positions[i+1]
    mid_x = (start_x + end_x) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid_x, 0, bottom_chord_z))
    bottom_segment = bpy.context.active_object
    bottom_segment.name = f"bottom_chord_{i}"
    bottom_segment.scale = (bay_length, beam_cross_section, beam_cross_section)
    bpy.ops.rigidbody.object_add()
    bottom_segment.rigid_body.type = 'PASSIVE'
    beam_objects.append(bottom_segment)

# Create vertical members (5 total, at interior nodes)
for i in range(1, num_bays):  # Skip first and last nodes
    x_pos = node_x_positions[i]
    mid_z = (top_chord_z + bottom_chord_z) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, mid_z))
    vertical = bpy.context.active_object
    vertical.name = f"vertical_{i}"
    vertical.scale = (beam_cross_section, beam_cross_section, vertical_height)
    bpy.ops.rigidbody.object_add()
    vertical.rigid_body.type = 'PASSIVE'
    beam_objects.append(vertical)

# Create diagonal members (6 total)
diagonal_angles = math.atan2(truss_depth, bay_length)  # Angle from horizontal

# Left half diagonals (sloping down-right)
for i in range(num_bays//2):
    # From top left to bottom right
    top_x = node_x_positions[i]
    bottom_x = node_x_positions[i+1]
    mid_x = (top_x + bottom_x) / 2
    mid_z = (top_chord_z + bottom_chord_z) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid_x, 0, mid_z))
    diagonal = bpy.context.active_object
    diagonal.name = f"diagonal_L_{i}"
    diagonal.scale = (beam_cross_section, beam_cross_section, diagonal_length)
    diagonal.rotation_euler = (0, -diagonal_angles, 0)  # Negative rotation for down-right
    bpy.ops.rigidbody.object_add()
    diagonal.rigid_body.type = 'PASSIVE'
    beam_objects.append(diagonal)

# Right half diagonals (sloping down-left)
for i in range(num_bays//2, num_bays):
    # From top right to bottom left
    top_x = node_x_positions[i+1]
    bottom_x = node_x_positions[i]
    mid_x = (top_x + bottom_x) / 2
    mid_z = (top_chord_z + bottom_chord_z) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid_x, 0, mid_z))
    diagonal = bpy.context.active_object
    diagonal.name = f"diagonal_R_{i}"
    diagonal.scale = (beam_cross_section, beam_cross_section, diagonal_length)
    diagonal.rotation_euler = (0, diagonal_angles, 0)  # Positive rotation for down-left
    bpy.ops.rigidbody.object_add()
    diagonal.rigid_body.type = 'PASSIVE'
    beam_objects.append(diagonal)

# Create load plate at center of top chord
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, top_chord_z))
load_plate = bpy.context.active_object
load_plate.name = "load_plate"
load_plate.scale = load_plate_size
bpy.ops.rigidbody.object_add()
load_plate.rigid_body.mass = load_mass
load_plate.rigid_body.type = 'ACTIVE'

# Create fixed constraints between adjacent elements
def create_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"constraint_{obj_a.name}_{obj_b.name}"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# Connect top chord segments to joints
for i, segment in enumerate([obj for obj in beam_objects if "top_chord" in obj.name]):
    # Connect to left joint
    left_joint = next(j for j in joint_objects if f"top_joint_{i}" in j.name)
    create_fixed_constraint(segment, left_joint)
    
    # Connect to right joint
    right_joint = next(j for j in joint_objects if f"top_joint_{i+1}" in j.name)
    create_fixed_constraint(segment, right_joint)

# Connect bottom chord segments to joints
for i, segment in enumerate([obj for obj in beam_objects if "bottom_chord" in obj.name]):
    left_joint = next(j for j in joint_objects if f"bottom_joint_{i}" in j.name)
    create_fixed_constraint(segment, left_joint)
    
    right_joint = next(j for j in joint_objects if f"bottom_joint_{i+1}" in j.name)
    create_fixed_constraint(segment, right_joint)

# Connect vertical members to joints
for i in range(1, num_bays):
    vertical = next(obj for obj in beam_objects if f"vertical_{i}" in obj.name)
    top_joint = next(j for j in joint_objects if f"top_joint_{i}" in j.name)
    bottom_joint = next(j for j in joint_objects if f"bottom_joint_{i}" in j.name)
    
    create_fixed_constraint(vertical, top_joint)
    create_fixed_constraint(vertical, bottom_joint)

# Connect diagonal members to joints
# Left diagonals
for i in range(num_bays//2):
    diagonal = next(obj for obj in beam_objects if f"diagonal_L_{i}" in obj.name)
    top_joint = next(j for j in joint_objects if f"top_joint_{i}" in j.name)
    bottom_joint = next(j for j in joint_objects if f"bottom_joint_{i+1}" in j.name)
    
    create_fixed_constraint(diagonal, top_joint)
    create_fixed_constraint(diagonal, bottom_joint)

# Right diagonals
for i in range(num_bays//2, num_bays):
    diagonal = next(obj for obj in beam_objects if f"diagonal_R_{i}" in obj.name)
    top_joint = next(j for j in joint_objects if f"top_joint_{i+1}" in j.name)
    bottom_joint = next(j for j in joint_objects if f"bottom_joint_{i}" in j.name)
    
    create_fixed_constraint(diagonal, top_joint)
    create_fixed_constraint(diagonal, bottom_joint)

# Fix load plate to top chord center joint
center_joint = next(j for j in joint_objects if "top_joint_3" in j.name)
create_fixed_constraint(load_plate, center_joint)

# Configure physics simulation
bpy.context.scene.frame_end = simulation_frames
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Howe Truss construction complete. Ready for simulation.")
print(f"Design specifications:")
print(f"- Span: {span_length}m, Depth: {truss_depth}m")
print(f"- Central load: {load_mass}kg ({load_mass*9.81/1000:.1f}kN)")
print(f"- Maximum allowable displacement: {max_displacement}m")
print(f"- Simulation frames: {simulation_frames}")