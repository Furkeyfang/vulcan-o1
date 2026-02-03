import bpy
import mathutils

# ====================
# PARAMETERS
# ====================
num_levels = 7
level_interval = 3.0
platform_width = 4.0
platform_thickness = 0.5
column_width = 0.5
column_height = 3.0
load_cube_size = 1.0
load_mass = 1400.0

platform_centers = [(0.0, 0.0, level_interval * i + 0.5) for i in range(num_levels)]
column_center_z = [level_interval * i + 2.0 for i in range(num_levels - 1)]
corner_offsets = [
    (1.75, 1.75),
    (1.75, -1.75),
    (-1.75, 1.75),
    (-1.75, -1.75)
]
load_cube_center = (0.0, 0.0, 21.0)

# ====================
# SCENE SETUP
# ====================
# Clear existing
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# ====================
# CREATE PLATFORMS
# ====================
platform_objects = []
for i, center in enumerate(platform_centers):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    plat = bpy.context.active_object
    plat.name = f"Platform_{i}"
    plat.scale = (platform_width, platform_width, platform_thickness)
    bpy.ops.rigidbody.object_add()
    # First platform is passive anchor, others are active
    plat.rigid_body.type = 'PASSIVE' if i == 0 else 'ACTIVE'
    plat.rigid_body.collision_shape = 'BOX'
    platform_objects.append(plat)

# ====================
# CREATE COLUMNS
# ====================
column_objects = []
for level in range(num_levels - 1):
    z = column_center_z[level]
    for j, (dx, dy) in enumerate(corner_offsets):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(dx, dy, z))
        col = bpy.context.active_object
        col.name = f"Column_{level}_{j}"
        col.scale = (column_width, column_width, column_height)
        bpy.ops.rigidbody.object_add()
        col.rigid_body.type = 'ACTIVE'
        col.rigid_body.collision_shape = 'BOX'
        column_objects.append(col)

# ====================
# FIXED CONSTRAINTS
# ====================
# Platform ↔ Column constraints
for level in range(num_levels - 1):
    platform_below = platform_objects[level]
    platform_above = platform_objects[level + 1]
    for j in range(4):
        col = column_objects[level * 4 + j]
        
        # Constraint: Platform_below → Column
        const1 = platform_below.constraints.new(type='RIGID_BODY_JOINT')
        const1.object1 = platform_below
        const1.object2 = col
        const1.type = 'FIXED'
        
        # Constraint: Column → Platform_above
        const2 = col.constraints.new(type='RIGID_BODY_JOINT')
        const2.object1 = col
        const2.object2 = platform_above
        const2.type = 'FIXED'

# ====================
# LOAD CUBE
# ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_cube_center)
load_cube = bpy.context.active_object
load_cube.name = "Load_Cube"
load_cube.scale = (load_cube_size, load_cube_size, load_cube_size)
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass
load_cube.rigid_body.collision_shape = 'BOX'

# Constraint: Top platform → Load cube
top_platform = platform_objects[-1]
const_load = top_platform.constraints.new(type='RIGID_BODY_JOINT')
const_load.object1 = top_platform
const_load.object2 = load_cube
const_load.type = 'FIXED'

# ====================
# VERIFICATION SETUP
# ====================
# Set simulation end frame
bpy.context.scene.frame_end = 100
# Ensure proper collision margins (optional)
for obj in bpy.context.scene.objects:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.0

print("Scaffold construction complete.")