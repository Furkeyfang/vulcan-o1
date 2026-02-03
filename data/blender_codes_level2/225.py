import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Parameters from summary
span_length = 11.0
truss_height = 2.0
member_cs = 0.2
bottom_z = 0.0
skylight_width = 3.0
queen_post_height = 1.5
queen_post_x = [-2.75, 2.75]
diag_brace_len = 3.286
top_seg_len = 4.0
top_left_center_x = -3.5
top_right_center_x = 3.5
total_load = 7848.0
load_per_segment = 3924.0
frames = 100
queen_post_bottom_z = 0.1
queen_post_top_z = 1.6
top_chord_bottom_z = 1.9

# Create Bottom Chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, bottom_z))
bottom_chord = bpy.context.active_object
bottom_chord.name = "Bottom_Chord"
bottom_chord.scale = (span_length, member_cs, member_cs)
bpy.ops.rigidbody.object_add()
bottom_chord.rigid_body.type = 'PASSIVE'
bottom_chord.rigid_body.collision_shape = 'BOX'

# Create Top Chord Left Segment
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(top_left_center_x, 0.0, truss_height))
top_left = bpy.context.active_object
top_left.name = "Top_Chord_Left"
top_left.scale = (top_seg_len, member_cs, member_cs)
bpy.ops.rigidbody.object_add()
top_left.rigid_body.mass = 100.0  # kg
top_left.rigid_body.collision_shape = 'BOX'

# Create Top Chord Right Segment
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(top_right_center_x, 0.0, truss_height))
top_right = bpy.context.active_object
top_right.name = "Top_Chord_Right"
top_right.scale = (top_seg_len, member_cs, member_cs)
bpy.ops.rigidbody.object_add()
top_right.rigid_body.mass = 100.0
top_right.rigid_body.collision_shape = 'BOX'

# Create Queen Posts
queen_posts = []
for i, x_pos in enumerate(queen_post_x):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0.0, queen_post_bottom_z + queen_post_height/2))
    qp = bpy.context.active_object
    qp.name = f"Queen_Post_{i+1}"
    qp.scale = (member_cs, member_cs, queen_post_height)
    bpy.ops.rigidbody.object_add()
    qp.rigid_body.mass = 50.0
    qp.rigid_body.collision_shape = 'BOX'
    queen_posts.append(qp)

# Create Diagonal Braces
# Left diagonal: from (-5.5, 0, 0.1) to (-2.75, 0, 1.9)
diag_start_left = Vector((-5.5, 0.0, queen_post_bottom_z))
diag_end_left = Vector((-2.75, 0.0, top_chord_bottom_z))
diag_center_left = (diag_start_left + diag_end_left) / 2
diag_dir_left = (diag_end_left - diag_start_left).normalized()

bpy.ops.mesh.primitive_cube_add(size=1.0, location=diag_center_left)
diag_left = bpy.context.active_object
diag_left.name = "Diagonal_Brace_Left"
# Scale: cross-section in XY, length in Z
diag_left.scale = (member_cs, member_cs, diag_brace_len)
# Rotate to align with direction
angle = math.atan2(diag_dir_left.z, diag_dir_left.x)
diag_left.rotation_euler = (0.0, -angle, 0.0)
bpy.ops.rigidbody.object_add()
diag_left.rigid_body.mass = 40.0
diag_left.rigid_body.collision_shape = 'BOX'

# Right diagonal: from (5.5, 0, 0.1) to (2.75, 0, 1.9)
diag_start_right = Vector((5.5, 0.0, queen_post_bottom_z))
diag_end_right = Vector((2.75, 0.0, top_chord_bottom_z))
diag_center_right = (diag_start_right + diag_end_right) / 2
diag_dir_right = (diag_end_right - diag_start_right).normalized()

bpy.ops.mesh.primitive_cube_add(size=1.0, location=diag_center_right)
diag_right = bpy.context.active_object
diag_right.name = "Diagonal_Brace_Right"
diag_right.scale = (member_cs, member_cs, diag_brace_len)
angle = math.atan2(diag_dir_right.z, diag_dir_right.x)
diag_right.rotation_euler = (0.0, -angle, 0.0)
bpy.ops.rigidbody.object_add()
diag_right.rigid_body.mass = 40.0
diag_right.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints
def create_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object2 = obj_b
    constraint.disable_collisions = True

# Connect queen posts to bottom chord
for qp in queen_posts:
    create_fixed_constraint(qp, bottom_chord)

# Connect top chord segments to queen posts (via diagonal endpoints)
# Left side: top_left connects to queen_post[0] and diag_left
create_fixed_constraint(top_left, queen_posts[0])
create_fixed_constraint(top_left, diag_left)

# Right side: top_right connects to queen_post[1] and diag_right
create_fixed_constraint(top_right, queen_posts[1])
create_fixed_constraint(top_right, diag_right)

# Connect diagonals to bottom chord
create_fixed_constraint(diag_left, bottom_chord)
create_fixed_constraint(diag_right, bottom_chord)

# Apply distributed load as constant force on top chord segments
# Force = mass * acceleration, but we apply direct force in Newtons
# Divide by mass to get acceleration for rigid body force
top_left.rigid_body.constant_force = (0.0, 0.0, -load_per_segment)
top_right.rigid_body.constant_force = (0.0, 0.0, -load_per_segment)

# Set simulation frames
bpy.context.scene.frame_end = frames

# Bake simulation (optional for verification)
# bpy.ops.ptcache.bake_all(bake=True)

print("Queen Post truss construction complete. Simulation ready.")