import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (6.0, 6.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
column_dim = (0.5, 0.5, 12.0)
column_offset_xy = 2.75
column_loc_z = 6.5
top_platform_dim = (6.0, 6.0, 0.5)
top_platform_loc = (0.0, 0.0, 12.75)
load_mass_kg = 3000.0
simulation_frames = 500
gravity = 9.8

# Set up physics world
bpy.context.scene.rigidbody_world.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Helper function to add cube with physics
def add_cube(name, location, scale, rigidbody_type='PASSIVE', mass=1.0, collision_shape='BOX'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigidbody_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = collision_shape
    obj.rigid_body.collision_margin = 0.0
    return obj

# 1. Base Frame (fixed to ground)
base = add_cube('Base', base_loc, base_dim, 'PASSIVE')

# 2. Four Vertical Columns
columns = []
corner_signs = [(1,1), (1,-1), (-1,1), (-1,-1)]
for i, (sx, sy) in enumerate(corner_signs):
    col_loc = (sx * column_offset_xy, sy * column_offset_xy, column_loc_z)
    col = add_cube(f'Column_{i}', col_loc, column_dim, 'PASSIVE')
    columns.append(col)

# 3. Top Platform (load-bearing)
top = add_cube('TopPlatform', top_platform_loc, top_platform_dim, 'ACTIVE', load_mass_kg)

# 4. Create Fixed Constraints between components
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body_constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.disable_collisions = True

# Base to each column
for col in columns:
    add_fixed_constraint(base, col)

# Each column to top platform
for col in columns:
    add_fixed_constraint(col, top)

# Ensure all objects are visible for simulation
for obj in [base, top] + columns:
    obj.hide_render = False
    obj.hide_viewport = False