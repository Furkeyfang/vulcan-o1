import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (5.0, 5.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
base_mass = 4000.0

col_dim = (0.5, 0.5, 15.0)
col_offset_xy = 2.25
col_centers = [
    (col_offset_xy, col_offset_xy, 7.75),
    (col_offset_xy, -col_offset_xy, 7.75),
    (-col_offset_xy, col_offset_xy, 7.75),
    (-col_offset_xy, -col_offset_xy, 7.75)
]
col_mass = 750.0

top_dim = (4.0, 4.0, 0.5)
top_loc = (0.0, 0.0, 14.75)
top_mass = 1000.0

load_dim = (0.5, 0.5, 0.5)
load_loc = (0.0, 0.0, 15.25)
load_mass = 400.0

simulation_frames = 500
gravity = -9.81

# Set gravity
bpy.context.scene.gravity = (0, 0, gravity)
bpy.context.scene.frame_end = simulation_frames

# Helper function to create rigid body
def add_rigidbody(obj, body_type='PASSIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1

# Helper function to create fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b, name="Fixed"):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{obj_a.name}_to_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    
    return constraint

# 1. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = base_dim
add_rigidbody(base, 'PASSIVE', base_mass)

# 2. Create Four Columns
columns = []
for i, center in enumerate(col_centers):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = col_dim
    add_rigidbody(col, 'PASSIVE', col_mass)
    columns.append(col)
    
    # Create fixed constraint between column and base
    add_fixed_constraint(col, base, f"Col{i+1}_to_Base")

# 3. Create Top Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=top_loc)
top = bpy.context.active_object
top.name = "Top_Platform"
top.scale = top_dim
add_rigidbody(top, 'PASSIVE', top_mass)

# Create fixed constraints between top platform and each column
for i, col in enumerate(columns):
    add_fixed_constraint(top, col, f"Top_to_Col{i+1}")

# 4. Create Load
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
add_rigidbody(load, 'ACTIVE', load_mass)

# Ensure all objects are visible in viewport
for obj in bpy.data.objects:
    obj.hide_viewport = False
    obj.hide_render = False

print("Tower construction complete. Structure ready for simulation.")