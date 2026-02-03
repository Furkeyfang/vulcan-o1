import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 14.0
cw = 0.3  # chord width (x)
ch = 0.3  # chord height (z)
pw = 0.3  # post width (x)
pd = 0.3  # post depth (y)
ph = 2.5  # post height (z)
top_z = 3.0
bot_z = 0.5
post1_x = -span/3.0  # -2.333
post2_x = span/3.0   # +2.333
left_x = -span/2.0   # -7.0
right_x = span/2.0   # +7.0
force = 9800.0
frames = 100

# Enable rigid body world
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Helper: create box with rigid body
def create_box(name, loc, scale, rb_type='ACTIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.mass = scale.x * scale.y * scale.z * 500  # density ~500 kg/m³
    return obj

# Create chords (horizontal)
top_chord = create_box("TopChord", (0,0,top_z), (span/2, cw/2, ch/2))
bot_chord = create_box("BottomChord", (0,0,bot_z), (span/2, cw/2, ch/2))

# Create queen posts (vertical)
post1 = create_box("Post1", (post1_x, 0, (top_z+bot_z)/2), (pw/2, pd/2, ph/2))
post2 = create_box("Post2", (post2_x, 0, (top_z+bot_z)/2), (pw/2, pd/2, ph/2))

# Create diagonal struts (via rotated boxes)
def create_diagonal(name, start, end):
    # Calculate midpoint and rotation
    mid = (mathutils.Vector(start) + mathutils.Vector(end)) / 2
    direction = mathutils.Vector(end) - mathutils.Vector(start)
    length = direction.length
    # Create cube at origin
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
    diag = bpy.context.active_object
    diag.name = name
    # Scale: length in x, 0.3 in y and z
    diag.scale = (length/2, 0.15, 0.15)
    # Rotate to align with direction
    up = mathutils.Vector((0,0,1))
    rot_quat = direction.to_track_quat('X', 'Z')
    diag.rotation_euler = rot_quat.to_euler()
    # Move to midpoint
    diag.location = mid
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.collision_shape = 'BOX'
    diag.rigid_body.mass = length * 0.3 * 0.3 * 500
    return diag

diag_left = create_diagonal("DiagLeft", 
                           (post1_x, 0, top_z), 
                           (left_x, 0, bot_z))
diag_right = create_diagonal("DiagRight", 
                            (post2_x, 0, top_z), 
                            (right_x, 0, bot_z))

# Create fixed constraints between connected members
def add_fixed_constraint(obj1, obj2, loc):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj1
    con.object2 = obj2

# Top chord to posts
add_fixed_constraint(top_chord, post1, (post1_x, 0, top_z))
add_fixed_constraint(top_chord, post2, (post2_x, 0, top_z))
# Bottom chord to posts
add_fixed_constraint(bot_chord, post1, (post1_x, 0, bot_z))
add_fixed_constraint(bot_chord, post2, (post2_x, 0, bot_z))
# Top chord to diagonals (at post tops)
add_fixed_constraint(top_chord, diag_left, (post1_x, 0, top_z))
add_fixed_constraint(top_chord, diag_right, (post2_x, 0, top_z))
# Bottom chord to diagonals (at supports)
add_fixed_constraint(bot_chord, diag_left, (left_x, 0, bot_z))
add_fixed_constraint(bot_chord, diag_right, (right_x, 0, bot_z))

# Apply downward force on top chord (uniform distribution)
# Create force field at top chord location
bpy.ops.object.effector_add(type='FORCE', location=(0,0,top_z))
force_field = bpy.context.active_object
force_field.name = "UniformLoad"
force_field.field.strength = -force  # Negative for downward
force_field.field.distance = 0.0  # Affects all vertices
force_field.field.use_max_distance = True
force_field.field.max_distance = 1.0  # Only affect nearby objects
# Limit to top chord via collision group (simplified)
force_field.field.falloff_type = 'TUBE'
force_field.field.flow = 0.0  # No air flow
# Keyframe force activation
force_field.field.strength = 0.0
force_field.keyframe_insert(data_path="field.strength", frame=1)
force_field.field.strength = -force
force_field.keyframe_insert(data_path="field.strength", frame=2)
force_field.keyframe_insert(data_path="field.strength", frame=frames)

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = frames