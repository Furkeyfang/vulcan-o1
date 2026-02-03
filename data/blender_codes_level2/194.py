import bpy
import math

# ========== PARAMETERS ==========
mast_height = 26.0
base_square = 2.0
column_width = 0.5
horizontal_interval = 2.0
horizontal_length = 2.0
horizontal_width = 0.3
diagonal_length = 2.828
diagonal_width = 0.3
platform_size = (3.0, 3.0, 0.5)
platform_z = 26.0
load_mass = 1400.0
load_cube_size = 1.0
collision_margin = 0.01

# Column positions (center at base of column)
col_positions = [
    ( base_square/2,  base_square/2, 0),
    ( base_square/2, -base_square/2, 0),
    (-base_square/2, -base_square/2, 0),
    (-base_square/2,  base_square/2, 0)
]

# ========== SCENE SETUP ==========
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# ========== CREATE VERTICAL COLUMNS ==========
columns = []
for i, pos in enumerate(col_positions):
    # Column center is at half height
    loc = (pos[0], pos[1], mast_height/2)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    col = bpy.context.active_object
    col.name = f"Column_{i}"
    col.scale = (column_width, column_width, mast_height)
    # Rigid body: passive with high mass
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    col.rigid_body.collision_margin = collision_margin
    col.rigid_body.mass = 1000  # Heavy base mass
    columns.append(col)

# ========== CREATE HORIZONTAL BRACING ==========
# Horizontal braces at each level (excluding top)
num_levels = int(mast_height / horizontal_interval)
for level in range(1, num_levels):
    z = level * horizontal_interval
    # North-South braces (between columns 0-1 and 2-3)
    for x_sign in [1, -1]:
        x = x_sign * base_square/2
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, z))
        brace = bpy.context.active_object
        brace.name = f"Horizontal_NS_x{x_sign}_z{z}"
        brace.scale = (horizontal_width, horizontal_length, horizontal_width)
        bpy.ops.rigidbody.object_add()
        brace.rigid_body.type = 'PASSIVE'
        brace.rigid_body.collision_margin = collision_margin
    # East-West braces (between columns 0-3 and 1-2)
    for y_sign in [1, -1]:
        y = y_sign * base_square/2
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y, z))
        brace = bpy.context.active_object
        brace.name = f"Horizontal_EW_y{y_sign}_z{z}"
        brace.scale = (horizontal_length, horizontal_width, horizontal_width)
        bpy.ops.rigidbody.object_add()
        brace.rigid_body.type = 'PASSIVE'
        brace.rigid_body.collision_margin = collision_margin

# ========== CREATE DIAGONAL BRACING ==========
# Diagonal braces in two vertical planes per bay
for level in range(num_levels - 1):
    z_bottom = level * horizontal_interval
    z_center = z_bottom + horizontal_interval/2
    # Plane 1: diagonal from (+1,+1) to (-1,-1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_center))
    diag1 = bpy.context.active_object
    diag1.name = f"Diagonal_1_z{z_bottom}"
    diag1.scale = (diagonal_width, diagonal_width, diagonal_length)
    diag1.rotation_euler = (0, math.radians(45), 0)
    bpy.ops.rigidbody.object_add()
    diag1.rigid_body.type = 'PASSIVE'
    diag1.rigid_body.collision_margin = collision_margin
    # Plane 2: diagonal from (+1,-1) to (-1,+1) - rotate 90° in horizontal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_center))
    diag2 = bpy.context.active_object
    diag2.name = f"Diagonal_2_z{z_bottom}"
    diag2.scale = (diagonal_width, diagonal_width, diagonal_length)
    diag2.rotation_euler = (0, math.radians(45), math.radians(90))
    bpy.ops.rigidbody.object_add()
    diag2.rigid_body.type = 'PASSIVE'
    diag2.rigid_body.collision_margin = collision_margin

# ========== CREATE TOP PLATFORM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, platform_z))
platform = bpy.context.active_object
platform.name = "TopPlatform"
platform.scale = platform_size
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.collision_margin = collision_margin

# ========== CREATE LOAD CUBE ==========
load_z = platform_z + platform_size[2]/2 + load_cube_size/2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_cube_size, load_cube_size, load_cube_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_margin = collision_margin
load.rigid_body.mass = load_mass

# ========== CREATE FIXED CONSTRAINTS ==========
# Utility function to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.rigid_body.constraints[-1]
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# Constraints between columns and ground (via empty anchor)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, -0.1))
anchor = bpy.context.active_object
anchor.name = "GroundAnchor"
bpy.ops.rigidbody.object_add()
anchor.rigid_body.type = 'PASSIVE'
for col in columns:
    add_fixed_constraint(col, anchor)

# Constraints between connected structural members (simplified: all to first column)
# In a full simulation, each connection would be individually constrained.
# For simplicity, we'll create a network: all horizontals/diagonals/platform constrained to columns.
all_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj != load]
for obj in all_objects:
    if obj not in columns:
        add_fixed_constraint(obj, columns[0])

print("Truss crane mast constructed. Run simulation for 100 frames to verify stability.")