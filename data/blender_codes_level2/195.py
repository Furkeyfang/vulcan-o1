import bpy
import mathutils

# ========== PARAMETERS ==========
col_size = 1.0
n_cubes = 21
plat_size = (3.0, 3.0, 0.5)
plat_heights = [7.0, 14.0]  # Top surface heights
load_size = 1.0
load_mass = 2500.0
load_z = 14.5
ground_size = 10.0
ground_z = -0.1
base_mass = 1000.0
gravity = -9.81

# ========== SCENE SETUP ==========
# Clear existing
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set gravity (headless compatible)
bpy.context.scene.gravity = (0, 0, gravity)

# ========== GROUND PLANE ==========
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, ground_z))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'
ground.rigid_body.use_margin = True
ground.rigid_body.collision_margin = 0.0

# ========== CENTRAL COLUMN ==========
column_cubes = []
for i in range(n_cubes):
    z_center = 0.5 + i  # Cube centers at 0.5, 1.5, ..., 20.5
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_center))
    cube = bpy.context.active_object
    cube.name = f"Column_Cube_{i:02d}"
    cube.scale = (col_size, col_size, col_size)
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.type = 'PASSIVE'
    cube.rigid_body.collision_shape = 'BOX'
    cube.rigid_body.use_margin = True
    cube.rigid_body.collision_margin = 0.0
    cube.rigid_body.mass = base_mass if i == 0 else 1.0  # Heavy base
    # Lock rotation for stability
    cube.rigid_body.kinematic = False
    cube.rigid_body.freeze_rotation_x = True
    cube.rigid_body.freeze_rotation_y = True
    cube.rigid_body.freeze_rotation_z = True
    column_cubes.append(cube)

# ========== FIXED CONSTRAINTS BETWEEN COLUMN CUBES ==========
for i in range(n_cubes - 1):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    empty = bpy.context.active_object
    empty.name = f"Fixed_Constraint_{i:02d}"
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = column_cubes[i]
    empty.rigid_body_constraint.object2 = column_cubes[i + 1]

# ========== PLATFORMS ==========
platforms = []
for i, height in enumerate(plat_heights):
    plat_center_z = height - (plat_size[2] / 2.0)  # Center so top surface at height
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, plat_center_z))
    plat = bpy.context.active_object
    plat.name = f"Platform_{height}m"
    plat.scale = plat_size
    bpy.ops.rigidbody.object_add()
    plat.rigid_body.type = 'PASSIVE'
    plat.rigid_body.collision_shape = 'BOX'
    plat.rigid_body.use_margin = True
    plat.rigid_body.collision_margin = 0.0
    # Lock rotation
    plat.rigid_body.freeze_rotation_x = True
    plat.rigid_body.freeze_rotation_y = True
    plat.rigid_body.freeze_rotation_z = True
    platforms.append(plat)
    
    # Attach platform to corresponding column cube
    # Column cube index = floor(height) because cubes span [n, n+1]
    col_index = int(math.floor(height))  # Cube from Z=height to height+1
    if col_index < n_cubes:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        empty = bpy.context.active_object
        empty.name = f"Platform_Constraint_{height}m"
        bpy.ops.rigidbody.constraint_add()
        empty.rigid_body_constraint.type = 'FIXED'
        empty.rigid_body_constraint.object1 = column_cubes[col_index]
        empty.rigid_body_constraint.object2 = plat

# ========== LOAD CUBE ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_z))
load = bpy.context.active_object
load.name = "Load_2500kg"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.use_margin = True
load.rigid_body.collision_margin = 0.0
load.rigid_body.mass = load_mass
# Load starts at rest (zero velocity)
load.rigid_body.enabled = True

# ========== FINAL SETTINGS ==========
bpy.context.scene.frame_end = 500
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50  # Increased for stability

print("Tower construction complete. Ready for simulation.")