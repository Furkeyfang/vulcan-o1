import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
H = 6.0
slab_xy = 4.0
slab_t = 0.5
col_norm = 0.5
col_soft = 0.25
half_grid = 2.0
mass_top = 1200.0
impulse_x = 2.0
frames = 100

# Derived positions
slab_z = [5.75, 11.75, 17.75]  # Centers
col_z = [3.0, 9.0, 15.0]       # Centers
corners = [(half_grid, half_grid), (half_grid, -half_grid),
           (-half_grid, half_grid), (-half_grid, -half_grid)]

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.frame_end = frames

# Create ground plane (passive)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Function to create column
def create_column(name, pos, height, size, story_num):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
    col = bpy.context.active_object
    col.name = name
    col.scale = (size, size, height)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.mass = height * size * size * 2400  # Concrete density
    col.rigid_body.collision_shape = 'BOX'
    return col

# Function to create slab
def create_slab(name, pos, size_xy, thickness, mass=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
    slab = bpy.context.active_object
    slab.name = name
    slab.scale = (size_xy, size_xy, thickness)
    bpy.ops.rigidbody.object_add()
    if mass:
        slab.rigid_body.mass = mass
    else:
        slab.rigid_body.mass = size_xy * size_xy * thickness * 2400
    slab.rigid_body.collision_shape = 'BOX'
    return slab

# Function to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    con = bpy.context.active_object
    con.name = f"Fix_{obj_a.name}_{obj_b.name}"
    con.rigid_body_constraint.type = 'FIXED'
    con.rigid_body_constraint.object1 = obj_a
    con.rigid_body_constraint.object2 = obj_b

# Level 1: Normal columns
cols_level1 = []
for i, (cx, cy) in enumerate(corners):
    col = create_column(f"Col_L1_{i}", (cx, cy, col_z[0]), H, col_norm, 1)
    cols_level1.append(col)
    add_fixed_constraint(col, ground)  # Base to ground

# Level 1 slab
slab1 = create_slab("Slab_L1", (0, 0, slab_z[0]), slab_xy, slab_t)
for col in cols_level1:
    add_fixed_constraint(col, slab1)  # Column tops to slab

# Level 2: Soft-story columns
cols_level2 = []
for i, (cx, cy) in enumerate(corners):
    col = create_column(f"Col_L2_{i}", (cx, cy, col_z[1]), H, col_soft, 2)
    cols_level2.append(col)
    add_fixed_constraint(col, slab1)  # Base to slab1

# Level 2 slab
slab2 = create_slab("Slab_L2", (0, 0, slab_z[1]), slab_xy, slab_t)
for col in cols_level2:
    add_fixed_constraint(col, slab2)  # Column tops to slab

# Level 3: Normal columns
cols_level3 = []
for i, (cx, cy) in enumerate(corners):
    col = create_column(f"Col_L3_{i}", (cx, cy, col_z[2]), H, col_norm, 3)
    cols_level3.append(col)
    add_fixed_constraint(col, slab2)  # Base to slab2

# Level 3 slab with mass
slab3 = create_slab("Slab_L3", (0, 0, slab_z[2]), slab_xy, slab_t, mass_top)
for col in cols_level3:
    add_fixed_constraint(col, slab3)  # Column tops to slab

# Apply lateral impulse to top slab (initial velocity)
slab3.rigid_body.kinematic = False
slab3.rigid_body.use_deactivation = False
slab3.rigid_body.linear_velocity = (impulse_x, 0.0, 0.0)

# Set collision margins for stability
for obj in bpy.data.objects:
    if hasattr(obj, 'rigid_body') and obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

# Bake simulation (headless compatible)
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = frames
bpy.ops.ptcache.bake_all(bake=True)