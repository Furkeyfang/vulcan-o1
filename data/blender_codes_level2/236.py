import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
span = 4.0
mem_cs = 0.2
brace_cs = 0.15
pitch_deg = 30.0
height = span/2 * math.tan(math.radians(pitch_deg))
top_len = math.sqrt((span/2)**2 + height**2)
apex = (0.0, 0.0, height)
bot_center = (0.0, 0.0, 0.0)
bot_left = (-span/2, 0.0, 0.0)
bot_right = (span/2, 0.0, 0.0)
king_ht = height
brace_attach_z = height / 3.0
t_param = 2.0/3.0
brace_left = (-span/2 * (1 - t_param), 0.0, height * t_param)
brace_right = (span/2 * (1 - t_param), 0.0, height * t_param)
brace_len = math.sqrt((brace_left[0]**2) + (brace_left[2] - brace_attach_z)**2)
load_mass = 150.0

# Helper: create beam with rigid body
def create_beam(name, size, location, rotation=None, scale=None, passive=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if scale:
        obj.scale = scale
    if rotation:
        obj.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE' if passive else 'ACTIVE'
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Helper: create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b, name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    const = empty.rigid_body_constraint
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# 1. Bottom Chord
bot_scale = (span, mem_cs, mem_cs)
bottom_chord = create_beam("BottomChord", 1.0, bot_center, scale=bot_scale)

# 2. Top Chord Left
angle_left = math.atan2(height, span/2)
top_left = create_beam("TopChordLeft", 1.0, bot_left, 
                       rotation=(0.0, -angle_left, 0.0),
                       scale=(top_len, mem_cs, mem_cs))

# 3. Top Chord Right
angle_right = math.atan2(height, -span/2)  # Negative because mirror
top_right = create_beam("TopChordRight", 1.0, bot_right,
                        rotation=(0.0, -angle_right, 0.0),
                        scale=(top_len, mem_cs, mem_cs))

# 4. King Post
king_scale = (mem_cs, mem_cs, king_ht)
king_post = create_beam("KingPost", 1.0, (0.0, 0.0, king_ht/2), scale=king_scale)

# 5. Diagonal Brace Left
brace_dir = (brace_left[0], 0.0, brace_left[2] - brace_attach_z)
brace_angle = math.atan2(brace_dir[2], brace_dir[0])
brace_pos = ((brace_left[0])/2, 0.0, (brace_left[2] + brace_attach_z)/2)
brace_scale = (brace_len, brace_cs, brace_cs)
braceL = create_beam("BraceLeft", 1.0, brace_pos,
                     rotation=(0.0, -brace_angle, 0.0),
                     scale=brace_scale)

# 6. Diagonal Brace Right
brace_dir_r = (brace_right[0], 0.0, brace_right[2] - brace_attach_z)
brace_angle_r = math.atan2(brace_dir_r[2], brace_dir_r[0])
brace_pos_r = ((brace_right[0])/2, 0.0, (brace_right[2] + brace_attach_z)/2)
braceR = create_beam("BraceRight", 1.0, brace_pos_r,
                     rotation=(0.0, -brace_angle_r, 0.0),
                     scale=brace_scale)

# 7. Load Mass (small cube at apex)
bpy.ops.mesh.primitive_cube_add(size=0.1, location=apex)
load = bpy.context.active_object
load.name = "LoadMass"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints at joints
# Apex: TopChordLeft, TopChordRight, KingPost, LoadMass
create_fixed_constraint(top_left, load, "Apex_LeftTop")
create_fixed_constraint(top_right, load, "Apex_RightTop")
create_fixed_constraint(king_post, load, "Apex_King")
# Bottom ends: Top chords to bottom chord
create_fixed_constraint(bottom_chord, top_left, "Joint_LeftBase")
create_fixed_constraint(bottom_chord, top_right, "Joint_RightBase")
# King Post base to bottom chord midpoint
create_fixed_constraint(bottom_chord, king_post, "Joint_KingBase")
# Braces: left brace to king post and top chord
create_fixed_constraint(king_post, braceL, "Joint_KingBraceL")
create_fixed_constraint(top_left, braceL, "Joint_TopBraceL")
# Braces: right brace to king post and top chord
create_fixed_constraint(king_post, braceR, "Joint_KingBraceR")
create_fixed_constraint(top_right, braceR, "Joint_TopBraceR")

# Configure rigid body world for static simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Run simulation (headless will execute when rendering or running script with --render)