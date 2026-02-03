import bpy
import math
from mathutils import Matrix, Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=True)

# Extract parameters from summary
span = 4.5
top_z = 3.0
cross = 0.1
post_h = 1.5
chord_hz = 2.25
chord_vt = 1.5
chord_len = 2.704

top_center = (0.0, 0.0, top_z)
post_top = (0.0, 0.0, top_z)
post_bottom = (0.0, 0.0, top_z - post_h)
post_center = (0.0, 0.0, (top_z + (top_z - post_h)) / 2)
left_end = (-span/2, 0.0, top_z)
right_end = (span/2, 0.0, top_z)

left_sup = (-span/2, 0.0, top_z - 0.05)
right_sup = (span/2, 0.0, top_z - 0.05)

load_m = 200.0
load_sz = 0.3
load_pos = (0.0, 0.0, top_z + 0.05)

density = 500.0
col_margin = 0.001

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.point_cache.frame_end = 100

# Helper function to create rigid body with consistent settings
def make_rigidbody(obj, body_type='ACTIVE', mass=1.0, collision_margin=col_margin):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_margin = collision_margin
    obj.rigid_body.collision_shape = 'BOX'

# 1. Create top chord
bpy.ops.mesh.primitive_cube_add(size=1, location=top_center)
top = bpy.context.active_object
top.name = "Top_Chord"
top.scale = (span/2, cross/2, cross/2)  # Default cube is 2 units wide
make_rigidbody(top, mass=density * span * cross * cross)

# 2. Create king post
bpy.ops.mesh.primitive_cube_add(size=1, location=post_center)
post = bpy.context.active_object
post.name = "King_Post"
post.scale = (cross/2, cross/2, post_h/2)
make_rigidbody(post, mass=density * post_h * cross * cross)

# 3. Create left bottom chord
# Calculate rotation angle
angle = math.atan2(chord_vt, chord_hz)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
left_chord = bpy.context.active_object
left_chord.name = "Left_Bottom_Chord"
left_chord.scale = (chord_len/2, cross/2, cross/2)
left_chord.rotation_euler = (0, -angle, 0)
# Position: midpoint between left top end and king post bottom
mid_x = (left_end[0] + post_bottom[0]) / 2
mid_z = (left_end[2] + post_bottom[2]) / 2
left_chord.location = (mid_x, 0.0, mid_z)
make_rigidbody(left_chord, mass=density * chord_len * cross * cross)

# 4. Create right bottom chord (mirrored)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
right_chord = bpy.context.active_object
right_chord.name = "Right_Bottom_Chord"
right_chord.scale = (chord_len/2, cross/2, cross/2)
right_chord.rotation_euler = (0, angle, 0)
mid_x = (right_end[0] + post_bottom[0]) / 2
mid_z = (right_end[2] + post_bottom[2]) / 2
right_chord.location = (mid_x, 0.0, mid_z)
make_rigidbody(right_chord, mass=density * chord_len * cross * cross)

# 5. Create supports
bpy.ops.mesh.primitive_cube_add(size=1, location=left_sup)
left_support = bpy.context.active_object
left_support.name = "Left_Support"
left_support.scale = (0.15, 0.15, 0.05)
make_rigidbody(left_support, body_type='PASSIVE')

bpy.ops.mesh.primitive_cube_add(size=1, location=right_sup)
right_support = bpy.context.active_object
right_support.name = "Right_Support"
right_support.scale = (0.15, 0.15, 0.05)
make_rigidbody(right_support, body_type='PASSIVE')

# 6. Create load
bpy.ops.mesh.primitive_cube_add(size=1, location=load_pos)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_sz/2, load_sz/2, load_sz/2)
make_rigidbody(load, mass=load_m)

# 7. Create fixed constraints
def add_fixed_constraint(obj1, obj2, name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2

# Connect top chord to king post (midpoint)
add_fixed_constraint(top, post, "Constraint_Top_Post")

# Connect left bottom chord to top chord and king post
add_fixed_constraint(top, left_chord, "Constraint_Top_LeftChord")
add_fixed_constraint(post, left_chord, "Constraint_Post_LeftChord")

# Connect right bottom chord to top chord and king post
add_fixed_constraint(top, right_chord, "Constraint_Top_RightChord")
add_fixed_constraint(post, right_chord, "Constraint_Post_RightChord")

# Connect supports to top chord
add_fixed_constraint(left_support, top, "Constraint_LeftSupport")
add_fixed_constraint(right_support, top, "Constraint_RightSupport")

# 8. Set up simulation
bpy.context.scene.frame_end = 100
print("King Post truss construction complete. Run simulation for 100 frames.")