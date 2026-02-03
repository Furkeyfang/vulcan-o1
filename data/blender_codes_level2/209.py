import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 5.0
bottom_chord_size = (5.0, 0.2, 0.2)
bottom_chord_loc = (0.0, 0.0, 0.0)
king_post_size = (0.2, 0.2, 1.5)
king_post_base_z = 0.1
king_post_center_z = 0.85
king_post_top_z = 2.35
top_chord_length = 3.36
top_chord_cross = (0.2, 0.2)
strut_length = 1.68
strut_cross = (0.2, 0.2)
load_force = 2452.5
load_point = (0.0, 0.0, 2.35)

# Enable rigid body physics
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Helper: Create cube with rigid body
def create_member(name, size, location, rotation=(0,0,0), rigid_type='ACTIVE', mass=50):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_type
    obj.rigid_body.mass = mass
    obj.rigid_body.restitution = 0.1
    obj.rigid_body.friction = 0.5
    return obj

# Helper: Create fixed constraint between two objects at world location
def create_fixed_constraint(name, obj_a, obj_b, location):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj_a
    con.object2 = obj_b

# 1. Bottom Chord (Passive foundation)
bottom_chord = create_member("Bottom_Chord", bottom_chord_size, bottom_chord_loc, rigid_type='PASSIVE', mass=0)

# 2. King Post (centered at calculated height)
king_post = create_member("King_Post", king_post_size, (0,0,king_post_center_z), rigid_type='ACTIVE', mass=30)

# 3. Left Top Chord
# Calculate rotation to point from left end to post top
start_left = Vector((-span/2, 0, king_post_base_z))
end = Vector(load_point)
vec_left = end - start_left
length_left = vec_left.length
angle_z_left = math.atan2(vec_left.y, vec_left.x) - math.pi/2
angle_y_left = math.atan2(vec_left.z, (vec_left.x**2 + vec_left.y**2)**0.5)
# Scale chord to actual length
top_chord_scale = (top_chord_length, top_chord_cross[0], top_chord_cross[1])
top_chord_left = create_member("Top_Chord_Left", 
                               top_chord_scale,
                               location=(start_left + end)/2,
                               rotation=(0, angle_y_left, angle_z_left),
                               mass=20)

# 4. Right Top Chord (mirrored)
start_right = Vector((span/2, 0, king_post_base_z))
vec_right = end - start_right
angle_z_right = math.atan2(vec_right.y, vec_right.x) - math.pi/2
angle_y_right = math.atan2(vec_right.z, (vec_right.x**2 + vec_right.y**2)**0.5)
top_chord_right = create_member("Top_Chord_Right",
                                top_chord_scale,
                                location=(start_right + end)/2,
                                rotation=(0, angle_y_right, angle_z_right),
                                mass=20)

# 5. Left Diagonal Strut
strut_start = Vector((-span/2, 0, king_post_base_z))
strut_mid = (start_left + end)/2
vec_strut = strut_mid - strut_start
length_strut = vec_strut.length
angle_z_strut = math.atan2(vec_strut.y, vec_strut.x) - math.pi/2
angle_y_strut = math.atan2(vec_strut.z, (vec_strut.x**2 + vec_strut.y**2)**0.5)
strut_scale = (strut_length, strut_cross[0], strut_cross[1])
strut_left = create_member("Strut_Left",
                           strut_scale,
                           location=(strut_start + strut_mid)/2,
                           rotation=(0, angle_y_strut, angle_z_strut),
                           mass=15)

# 6. Right Diagonal Strut (mirrored)
strut_start_r = Vector((span/2, 0, king_post_base_z))
strut_mid_r = (start_right + end)/2
vec_strut_r = strut_mid_r - strut_start_r
angle_z_strut_r = math.atan2(vec_strut_r.y, vec_strut_r.x) - math.pi/2
angle_y_strut_r = math.atan2(vec_strut_r.z, (vec_strut_r.x**2 + vec_strut_r.y**2)**0.5)
strut_right = create_member("Strut_Right",
                            strut_scale,
                            location=(strut_start_r + strut_mid_r)/2,
                            rotation=(0, angle_y_strut_r, angle_z_strut_r),
                            mass=15)

# Create fixed constraints at all joints
# Bottom chord to king post
create_fixed_constraint("Fix_Bottom_Post", bottom_chord, king_post, (0,0,king_post_base_z))
# Bottom chord to top chords
create_fixed_constraint("Fix_Bottom_ChordL", bottom_chord, top_chord_left, tuple(start_left))
create_fixed_constraint("Fix_Bottom_ChordR", bottom_chord, top_chord_right, tuple(start_right))
# King post to top chords
create_fixed_constraint("Fix_Post_ChordL", king_post, top_chord_left, tuple(end))
create_fixed_constraint("Fix_Post_ChordR", king_post, top_chord_right, tuple(end))
# Strut connections
create_fixed_constraint("Fix_Bottom_StrutL", bottom_chord, strut_left, tuple(strut_start))
create_fixed_constraint("Fix_Chord_StrutL", top_chord_left, strut_left, tuple(strut_mid))
create_fixed_constraint("Fix_Bottom_StrutR", bottom_chord, strut_right, tuple(strut_start_r))
create_fixed_constraint("Fix_Chord_StrutR", top_chord_right, strut_right, tuple(strut_mid_r))

# Apply downward force at king post top using force field
bpy.ops.object.effector_add(type='FORCE', location=load_point)
force = bpy.context.active_object
force.name = "Load_Force"
force.field.strength = load_force
force.field.direction = 'NEGATIVE_Z'
force.field.use_max_distance = True
force.field.distance_max = 0.5
force.field.falloff_power = 0

# Set collision margins for stability
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

# Set gravity to standard
bpy.context.scene.gravity = (0, 0, -9.81)