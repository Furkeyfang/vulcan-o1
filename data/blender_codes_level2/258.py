import bpy
import math

# ===== PARAMETERS =====
span_length = 20.0
chord_section = (0.3, 0.3)  # Y, Z cross-section
post_height = 2.0
post_section = (0.3, 0.3)   # X, Y cross-section
post_offset = 5.0           # from each end
roof_height = 2.0
load_mass = 2300.0
gravity = 9.81
sim_frames = 500

# Derived positions
half_span = span_length / 2.0
chord_length = span_length
post_x_left = post_offset
post_x_right = span_length - post_offset
bottom_z = 0.0
top_z = roof_height

# ===== SCENE SETUP =====
# Clear existing
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set gravity and simulation end
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.frame_end = sim_frames

# ===== FUNCTION: CREATE BEAM =====
def create_beam(name, size, location, rotation=(0,0,0)):
    """Create a cube beam with given dimensions and location"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2.0, size[1]/2.0, size[2]/2.0)  # cube radius=0.5
    if rotation != (0,0,0):
        obj.rotation_euler = rotation
    # Apply scale for physics accuracy
    bpy.ops.object.transform_apply(scale=True)
    return obj

# ===== CREATE TRUSS MEMBERS =====
# Bottom Chord (passive support)
bot_chord = create_beam(
    "Bottom_Chord",
    (chord_length, chord_section[0], chord_section[1]),
    (half_span, 0.0, bottom_z)
)
bpy.ops.rigidbody.object_add()
bot_chord.rigid_body.type = 'PASSIVE'
bot_chord.rigid_body.collision_shape = 'BOX'

# Top Chord (active, will carry load)
top_chord = create_beam(
    "Top_Chord",
    (chord_length, chord_section[0], chord_section[1]),
    (half_span, 0.0, top_z)
)
bpy.ops.rigidbody.object_add()
top_chord.rigid_body.type = 'ACTIVE'
top_chord.rigid_body.collision_shape = 'BOX'
top_chord.rigid_body.mass = 100.0  # Base mass (will add force separately)

# Queen Posts (vertical)
left_post = create_beam(
    "Left_Post",
    (post_section[0], post_section[1], post_height),
    (post_x_left, 0.0, post_height/2.0)
)
bpy.ops.rigidbody.object_add()
left_post.rigid_body.type = 'ACTIVE'
left_post.rigid_body.collision_shape = 'BOX'

right_post = create_beam(
    "Right_Post",
    (post_section[0], post_section[1], post_height),
    (post_x_right, 0.0, post_height/2.0)
)
bpy.ops.rigidbody.object_add()
right_post.rigid_body.type = 'ACTIVE'
right_post.rigid_body.collision_shape = 'BOX'

# Diagonal Struts (4 pieces)
# Geometry calculations
diag_length = math.sqrt(post_offset**2 + post_height**2)
diag_angle = math.atan2(post_height, post_offset)  # rad

# Top-Left diagonal (from left post top to left end of top chord)
diag_tl = create_beam(
    "Diagonal_TL",
    (diag_length, chord_section[0], chord_section[1]),
    (post_offset/2.0, 0.0, post_height/2.0 + 0.15),  # midpoint
    (0, -diag_angle, 0)  # rotate around Y-axis
)
bpy.ops.rigidbody.object_add()
diag_tl.rigid_body.type = 'ACTIVE'
diag_tl.rigid_body.collision_shape = 'BOX'

# Bottom-Left diagonal (from left post bottom to left end of bottom chord)
diag_bl = create_beam(
    "Diagonal_BL",
    (diag_length, chord_section[0], chord_section[1]),
    (post_offset/2.0, 0.0, 0.15),
    (0, diag_angle, 0)
)
bpy.ops.rigidbody.object_add()
diag_bl.rigid_body.type = 'ACTIVE'
diag_bl.rigid_body.collision_shape = 'BOX'

# Top-Right diagonal (from right post top to right end of top chord)
diag_tr = create_beam(
    "Diagonal_TR",
    (diag_length, chord_section[0], chord_section[1]),
    (span_length - post_offset/2.0, 0.0, post_height/2.0 + 0.15),
    (0, diag_angle, math.pi)  # mirrored
)
bpy.ops.rigidbody.object_add()
diag_tr.rigid_body.type = 'ACTIVE'
diag_tr.rigid_body.collision_shape = 'BOX'

# Bottom-Right diagonal (from right post bottom to right end of bottom chord)
diag_br = create_beam(
    "Diagonal_BR",
    (diag_length, chord_section[0], chord_section[1]),
    (span_length - post_offset/2.0, 0.0, 0.15),
    (0, -diag_angle, math.pi)  # mirrored
)
bpy.ops.rigidbody.object_add()
diag_br.rigid_body.type = 'ACTIVE'
diag_br.rigid_body.collision_shape = 'BOX'

# ===== APPLY LOAD FORCE =====
# Add force field downward on top chord (simulating distributed load)
bpy.ops.object.select_all(action='DESELECT')
top_chord.select_set(True)
bpy.context.view_layer.objects.active = top_chord
bpy.ops.object.forcefield_add(type='FORCE')
force_field = top_chord.field
force_field.strength = -load_mass * gravity  # Negative Z direction
force_field.falloff_power = 0  # Uniform
force_field.use_max_distance = False

# ===== CREATE FIXED CONSTRAINTS AT JOINTS =====
def add_fixed_constraint(obj_a, obj_b):
    """Create fixed constraint between two objects"""
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    const = bpy.context.active_object.rigid_body_constraint
    const.object2 = obj_b

# Connect bottom chord to posts
add_fixed_constraint(bot_chord, left_post)
add_fixed_constraint(bot_chord, right_post)

# Connect top chord to posts
add_fixed_constraint(top_chord, left_post)
add_fixed_constraint(top_chord, right_post)

# Connect diagonals to chords and posts
# Left side
add_fixed_constraint(diag_tl, left_post)
add_fixed_constraint(diag_tl, top_chord)
add_fixed_constraint(diag_bl, left_post)
add_fixed_constraint(diag_bl, bot_chord)
# Right side
add_fixed_constraint(diag_tr, right_post)
add_fixed_constraint(diag_tr, top_chord)
add_fixed_constraint(diag_br, right_post)
add_fixed_constraint(diag_br, bot_chord)

# ===== FINAL SETUP =====
# Enable rigid body visualization (optional)
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Queen Post truss assembly complete. Simulate with Alt+A.")