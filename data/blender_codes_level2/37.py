import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 9.0
height = 1.5
gap_y = 0.1
top_len = 4.5
top_w = 0.2
top_d = 0.2
bot_len = 4.5
bot_w = 0.2
bot_d = 0.2
vert_len = 1.5
vert_w = 0.15
vert_d = 0.15
diag_len = math.sqrt(4.5**2 + 1.5**2)  # 4.74341649
diag_w = 0.15
diag_d = 0.15
top_z = 1.5
bot_z = 0.0
left_x = -4.5
center_x = 0.0
right_x = 4.5
y_left = -gap_y/2  # -0.05
y_right = gap_y/2   # 0.05
force_total = 900 * 9.80665  # 8826 N
force_per_chord = force_total / 2  # 4413 N

# Helper function to create a rectangular beam
def create_beam(name, length, width, depth, location, rotation):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (length/2, width/2, depth/2)
    beam.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    return beam

# Create top chords (two parallel beams along X)
top_left = create_beam("TopChordLeft", top_len, top_w, top_d, 
                       (left_x/2, y_left, top_z), (0, 0, 0))
top_right = create_beam("TopChordRight", top_len, top_w, top_d,
                        (right_x/2, y_right, top_z), (0, 0, 0))

# Create bottom chords
bot_left = create_beam("BottomChordLeft", bot_len, bot_w, bot_d,
                       (left_x/2, y_left, bot_z), (0, 0, 0))
bot_right = create_beam("BottomChordRight", bot_len, bot_w, bot_d,
                        (right_x/2, y_right, bot_z), (0, 0, 0))

# Create vertical members (3)
vert_left = create_beam("VerticalLeft", vert_w, vert_d, vert_len,
                        (left_x, 0.0, (top_z + bot_z)/2), (0, math.pi/2, 0))
vert_center = create_beam("VerticalCenter", vert_w, vert_d, vert_len,
                          (center_x, 0.0, (top_z + bot_z)/2), (0, math.pi/2, 0))
vert_right = create_beam("VerticalRight", vert_w, vert_d, vert_len,
                         (right_x, 0.0, (top_z + bot_z)/2), (0, math.pi/2, 0))

# Create diagonal members (4)
# Left side diagonals
diag_left_top = create_beam("DiagonalLeftTop", diag_len, diag_w, diag_d,
                            ((left_x + center_x)/2, 0.0, (top_z + bot_z)/2),
                            (0, 0, math.atan2(-height, -4.5)))
diag_left_bot = create_beam("DiagonalLeftBottom", diag_len, diag_w, diag_d,
                            ((left_x + center_x)/2, 0.0, (top_z + bot_z)/2),
                            (0, 0, math.atan2(height, -4.5)))
# Right side diagonals (mirror)
diag_right_top = create_beam("DiagonalRightTop", diag_len, diag_w, diag_d,
                             ((center_x + right_x)/2, 0.0, (top_z + bot_z)/2),
                             (0, 0, math.atan2(-height, 4.5)))
diag_right_bot = create_beam("DiagonalRightBottom", diag_len, diag_w, diag_d,
                             ((center_x + right_x)/2, 0.0, (top_z + bot_z)/2),
                             (0, 0, math.atan2(height, 4.5)))

# Apply distributed load as constant force on top chords
top_left.rigid_body.enabled = True
top_right.rigid_body.enabled = True
# In Blender, constant force is applied via force fields or Python animation.
# We'll use a simple method: apply impulse every frame via handler (but for simplicity, we use a constant force field).
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 3))
force_empty = bpy.context.active_object
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = -force_per_chord  # Negative Z direction
force_empty.field.use_global_coords = True
# Link force field to top chords via parenting (simplified approach)
top_left.parent = force_empty
top_right.parent = force_empty

# Create fixed constraints at all joints
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Define joint connections (simplified: each beam end connects to others)
# In practice, you would compute exact joint positions and create constraints there.
# For brevity, we'll connect beams at their centers (approximation).
joints = [
    (top_left, vert_left),
    (top_left, diag_left_top),
    (top_left, diag_left_bot),
    (top_right, vert_right),
    (top_right, diag_right_top),
    (top_right, diag_right_bot),
    (bot_left, vert_left),
    (bot_left, diag_left_top),
    (bot_left, diag_left_bot),
    (bot_right, vert_right),
    (bot_right, diag_right_top),
    (bot_right, diag_right_bot),
    (vert_center, diag_left_top),
    (vert_center, diag_left_bot),
    (vert_center, diag_right_top),
    (vert_center, diag_right_bot),
    (vert_center, top_left),
    (vert_center, top_right),
    (vert_center, bot_left),
    (vert_center, bot_right)
]

for obj_a, obj_b in joints:
    add_fixed_constraint(obj_a, obj_b)

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Run simulation (headless rendering not required, but physics will bake)
print("Howe Truss constructed. Simulate with Rigid Body dynamics.")