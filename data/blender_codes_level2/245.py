import bpy
import math
from mathutils import Vector, Euler

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span_length = 16.0
truss_height = 2.5
chord_cross = 0.2
post_cross = 0.2
diagonal_cross = 0.15
left_post_x = span_length / 3.0
right_post_x = 2.0 * span_length / 3.0

bottom_chord_loc = (span_length / 2.0, 0.0, 0.0)
top_chord_loc = (span_length / 2.0, 0.0, truss_height)
left_post_loc = (left_post_x, 0.0, truss_height / 2.0)
right_post_loc = (right_post_x, 0.0, truss_height / 2.0)

diagonal_length = math.sqrt(left_post_x**2 + truss_height**2)
diagonal_angle = math.degrees(math.atan2(truss_height, left_post_x))

support_size = 0.3
left_support_loc = (0.0, 0.0, 0.0)
right_support_loc = (span_length, 0.0, 0.0)

total_load_mass = 1600.0
gravity = 9.81
total_force = total_load_mass * gravity

# Helper to add rigid body
def add_rigidbody(obj, body_type='ACTIVE'):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type

# Helper to create a fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.constraints[-1]
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# 1. Create Supports (Passive, fixed to world)
bpy.ops.mesh.primitive_cube_add(size=1, location=left_support_loc)
left_support = bpy.context.active_object
left_support.scale = (support_size, support_size, support_size)
add_rigidbody(left_support, 'PASSIVE')

bpy.ops.mesh.primitive_cube_add(size=1, location=right_support_loc)
right_support = bpy.context.active_object
right_support.scale = (support_size, support_size, support_size)
add_rigidbody(right_support, 'PASSIVE')

# 2. Create Bottom Chord
bpy.ops.mesh.primitive_cube_add(size=1, location=bottom_chord_loc)
bottom_chord = bpy.context.active_object
bottom_chord.scale = (span_length / 2.0, chord_cross / 2.0, chord_cross / 2.0)
add_rigidbody(bottom_chord, 'ACTIVE')

# 3. Create Top Chord
bpy.ops.mesh.primitive_cube_add(size=1, location=top_chord_loc)
top_chord = bpy.context.active_object
top_chord.scale = (span_length / 2.0, chord_cross / 2.0, chord_cross / 2.0)
add_rigidbody(top_chord, 'ACTIVE')

# 4. Create Queen Posts
bpy.ops.mesh.primitive_cube_add(size=1, location=left_post_loc)
left_post = bpy.context.active_object
left_post.scale = (post_cross / 2.0, post_cross / 2.0, truss_height / 2.0)
add_rigidbody(left_post, 'ACTIVE')

bpy.ops.mesh.primitive_cube_add(size=1, location=right_post_loc)
right_post = bpy.context.active_object
right_post.scale = (post_cross / 2.0, post_cross / 2.0, truss_height / 2.0)
add_rigidbody(right_post, 'ACTIVE')

# 5. Create Diagonal Braces
# Diagonal A: Bottom left to Left Post top
mid_a = Vector((left_post_x / 2.0, 0.0, truss_height / 2.0))
bpy.ops.mesh.primitive_cube_add(size=1, location=mid_a)
diag_a = bpy.context.active_object
diag_a.scale = (diagonal_cross / 2.0, diagonal_cross / 2.0, diagonal_length / 2.0)
diag_a.rotation_euler = Euler((0, math.radians(-diagonal_angle), 0), 'XYZ')
add_rigidbody(diag_a, 'ACTIVE')

# Diagonal B: Left Post bottom to Top left
mid_b = Vector((left_post_x / 2.0, 0.0, truss_height / 2.0))
bpy.ops.mesh.primitive_cube_add(size=1, location=mid_b)
diag_b = bpy.context.active_object
diag_b.scale = (diagonal_cross / 2.0, diagonal_cross / 2.0, diagonal_length / 2.0)
diag_b.rotation_euler = Euler((0, math.radians(diagonal_angle), 0), 'XYZ')
add_rigidbody(diag_b, 'ACTIVE')

# Diagonal C: Bottom right to Right Post top
mid_c = Vector((span_length - left_post_x / 2.0, 0.0, truss_height / 2.0))
bpy.ops.mesh.primitive_cube_add(size=1, location=mid_c)
diag_c = bpy.context.active_object
diag_c.scale = (diagonal_cross / 2.0, diagonal_cross / 2.0, diagonal_length / 2.0)
diag_c.rotation_euler = Euler((0, math.radians(diagonal_angle), 0), 'XYZ')
add_rigidbody(diag_c, 'ACTIVE')

# Diagonal D: Right Post bottom to Top right
mid_d = Vector((span_length - left_post_x / 2.0, 0.0, truss_height / 2.0))
bpy.ops.mesh.primitive_cube_add(size=1, location=mid_d)
diag_d = bpy.context.active_object
diag_d.scale = (diagonal_cross / 2.0, diagonal_cross / 2.0, diagonal_length / 2.0)
diag_d.rotation_euler = Euler((0, math.radians(-diagonal_angle), 0), 'XYZ')
add_rigidbody(diag_d, 'ACTIVE')

# 6. Apply Fixed Constraints at Joints
# Supports to Bottom Chord
add_fixed_constraint(left_support, bottom_chord)
add_fixed_constraint(right_support, bottom_chord)

# Bottom Chord to Queen Posts
add_fixed_constraint(bottom_chord, left_post)
add_fixed_constraint(bottom_chord, right_post)

# Top Chord to Queen Posts
add_fixed_constraint(top_chord, left_post)
add_fixed_constraint(top_chord, right_post)

# Diagonal A: (bottom left support, left post top, top chord left)
add_fixed_constraint(diag_a, left_support)
add_fixed_constraint(diag_a, left_post)
add_fixed_constraint(diag_a, top_chord)

# Diagonal B: (left post bottom, bottom chord left, top chord left)
add_fixed_constraint(diag_b, left_post)
add_fixed_constraint(diag_b, bottom_chord)
add_fixed_constraint(diag_b, top_chord)

# Diagonal C: (right support, right post top, top chord right)
add_fixed_constraint(diag_c, right_support)
add_fixed_constraint(diag_c, right_post)
add_fixed_constraint(diag_c, top_chord)

# Diagonal D: (right post bottom, bottom chord right, top chord right)
add_fixed_constraint(diag_d, right_post)
add_fixed_constraint(diag_d, bottom_chord)
add_fixed_constraint(diag_d, top_chord)

# 7. Apply Distributed Load on Top Chord
# Create a force field downward affecting only the top chord
bpy.ops.object.effector_add(type='FORCE', location=top_chord_loc)
force_field = bpy.context.active_object
force_field.field.strength = -total_force  # Negative for downward
force_field.field.falloff_power = 0  # Uniform
force_field.field.use_gravity = False
# Limit to top chord only by setting collision group
top_chord.rigid_body.collision_groups[0] = True
force_field.field.collision_group = 1 << 0  # Match group 0

# 8. Set up Rigid Body World
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# 9. Run Simulation (headless compatible)
# In headless mode, we can bake the simulation to keyframes for verification
bpy.ops.ptcache.bake_all(bake=True)