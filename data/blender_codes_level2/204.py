import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from parameter summary
span = 10.0
chord_length = 10.0
chord_width = 0.3
chord_height = 0.3
queen_post_offset = 2.5
queen_post_height = 2.0
queen_post_width = 0.3
queen_post_depth = 0.3
outer_diag_length = 3.202
inner_diag_length = 2.5
top_chord_z = 2.0
bottom_chord_z = 0.0
total_force_N = 6867.0
num_load_points = 10
force_per_point = 686.7
frame_count = 250

# Helper function to create a beam with rigid body physics
def create_beam(name, location, rotation, scale, rigid_type='ACTIVE'):
    # Create cube and transform
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_type
    obj.rigid_body.collision_shape = 'CONVEX_HULL'
    obj.rigid_body.mass = scale[0] * scale[1] * scale[2] * 2500  # Density ~2500 kg/m³ (concrete)
    return obj

# 1. Bottom chord (foundation, passive)
bottom_chord = create_beam(
    "BottomChord",
    location=(0.0, 0.0, bottom_chord_z),
    rotation=(0.0, 0.0, 0.0),
    scale=(chord_length, chord_width, chord_height),
    rigid_type='PASSIVE'
)

# 2. Top chord (active, will receive load)
top_chord = create_beam(
    "TopChord",
    location=(0.0, 0.0, top_chord_z),
    rotation=(0.0, 0.0, 0.0),
    scale=(chord_length, chord_width, chord_height),
    rigid_type='ACTIVE'
)

# 3. Queen posts (left and right)
queen_left = create_beam(
    "QueenPost_Left",
    location=(-queen_post_offset, 0.0, queen_post_height/2.0),
    rotation=(0.0, 0.0, 0.0),
    scale=(queen_post_width, queen_post_depth, queen_post_height),
    rigid_type='ACTIVE'
)

queen_right = create_beam(
    "QueenPost_Right",
    location=(queen_post_offset, 0.0, queen_post_height/2.0),
    rotation=(0.0, 0.0, 0.0),
    scale=(queen_post_width, queen_post_depth, queen_post_height),
    rigid_type='ACTIVE'
)

# 4. Outer diagonals (from queen top to bottom chord ends)
# Left outer diagonal: from (-2.5,0,2.0) to (-5,0,0)
outer_diag_left = create_beam(
    "OuterDiagonal_Left",
    location=(-3.75, 0.0, 1.0),  # midpoint
    rotation=(0.0, math.atan2(-queen_post_height, -2.5), 0.0),  # -2.5 X diff, -2.0 Z diff
    scale=(outer_diag_length, chord_width, chord_height),
    rigid_type='ACTIVE'
)

# Right outer diagonal: from (2.5,0,2.0) to (5,0,0)
outer_diag_right = create_beam(
    "OuterDiagonal_Right",
    location=(3.75, 0.0, 1.0),  # midpoint
    rotation=(0.0, math.atan2(-queen_post_height, 2.5), 0.0),  # 2.5 X diff, -2.0 Z diff
    scale=(outer_diag_length, chord_width, chord_height),
    rigid_type='ACTIVE'
)

# 5. Inner diagonals (horizontal from queen top to top chord center)
inner_diag_left = create_beam(
    "InnerDiagonal_Left",
    location=(-1.25, 0.0, top_chord_z),  # midpoint between queen left and center
    rotation=(0.0, 0.0, 0.0),
    scale=(inner_diag_length, chord_width, chord_height),
    rigid_type='ACTIVE'
)

inner_diag_right = create_beam(
    "InnerDiagonal_Right",
    location=(1.25, 0.0, top_chord_z),  # midpoint between queen right and center
    rotation=(0.0, 0.0, 0.0),
    scale=(inner_diag_length, chord_width, chord_height),
    rigid_type='ACTIVE'
)

# 6. Create fixed constraints for all joints
def create_fixed_constraint(obj_a, obj_b):
    # Create empty at midpoint for constraint
    mid_point = (
        (obj_a.location[0] + obj_b.location[0]) / 2,
        (obj_a.location[1] + obj_b.location[2]) / 2,
        (obj_a.location[2] + obj_b.location[2]) / 2
    )
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=mid_point)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Define joint connections based on truss topology
joint_pairs = [
    (bottom_chord, queen_left),
    (bottom_chord, queen_right),
    (top_chord, queen_left),
    (top_chord, queen_right),
    (top_chord, inner_diag_left),
    (top_chord, inner_diag_right),
    (queen_left, outer_diag_left),
    (queen_right, outer_diag_right),
    (bottom_chord, outer_diag_left),
    (bottom_chord, outer_diag_right),
    (queen_left, inner_diag_left),
    (queen_right, inner_diag_right)
]

for obj_a, obj_b in joint_pairs:
    create_fixed_constraint(obj_a, obj_b)

# 7. Apply distributed load on top chord
# Create small force applicators along top chord
for i in range(num_load_points):
    x_pos = -span/2 + (i + 0.5) * (span / num_load_points)  # center of each segment
    # Create small passive cube as force anchor
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(x_pos, 0.0, top_chord_z + 0.2))
    force_anchor = bpy.context.active_object
    force_anchor.name = f"ForcePoint_{i}"
    bpy.ops.rigidbody.object_add()
    force_anchor.rigid_body.type = 'PASSIVE'
    
    # Create fixed constraint between force anchor and top chord
    create_fixed_constraint(top_chord, force_anchor)
    
    # Apply downward force using rigid body force field
    bpy.ops.object.effector_add(type='FORCE', location=(x_pos, 0.0, top_chord_z + 0.5))
    force_field = bpy.context.active_object
    force_field.name = f"ForceField_{i}"
    force_field.field.strength = -force_per_point  # Negative for downward
    force_field.field.shape = 'POINT'
    force_field.field.use_max_distance = True
    force_field.field.distance_max = 0.3
    force_field.field.falloff_power = 0.0

# 8. Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = frame_count

# 9. Run simulation (in background mode this will be executed)
print("Queen Post truss created with distributed load. Simulation ready.")