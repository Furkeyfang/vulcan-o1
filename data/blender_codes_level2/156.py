import bpy

# ========== 1. Clear Scene ==========
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ========== 2. Define Variables ==========
# Base
base_dim = (8.0, 8.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

# Columns
column_dim = (0.5, 0.5, 10.0)
column_offset_xy = 3.75  # (8/2 - 0.5/2)
column_z_center = 5.5    # base top (0.5) + column_height/2 (5.0)

# Top Platform
top_dim = (8.0, 8.0, 0.5)
top_loc = (0.0, 0.0, 10.25)

# Load
load_mass_kg = 3000.0
load_dim = (1.0, 1.0, 1.0)
load_loc = (0.0, 0.0, 11.0)

# ========== 3. Create Base ==========
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# ========== 4. Create Four Columns ==========
column_locations = [
    ( column_offset_xy,  column_offset_xy, column_z_center),
    ( column_offset_xy, -column_offset_xy, column_z_center),
    (-column_offset_xy,  column_offset_xy, column_z_center),
    (-column_offset_xy, -column_offset_xy, column_z_center)
]
columns = []
for i, loc in enumerate(column_locations):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = column_dim
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    columns.append(col)

# ========== 5. Create Top Platform ==========
bpy.ops.mesh.primitive_cube_add(size=1, location=top_loc)
top = bpy.context.active_object
top.name = "TopPlatform"
top.scale = top_dim
bpy.ops.rigidbody.object_add()
top.rigid_body.type = 'PASSIVE'

# ========== 6. Add Fixed Constraints ==========
def add_fixed_constraint(obj_a, obj_b):
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj_a.name}_{obj_b.name}"
    constraint.location = ((obj_a.location.x + obj_b.location.x)/2,
                           (obj_a.location.y + obj_b.location.y)/2,
                           (obj_a.location.z + obj_b.location.z)/2)
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj_a
    rb_constraint.object2 = obj_b

# Base to each column
for col in columns:
    add_fixed_constraint(base, col)
# Each column to top platform
for col in columns:
    add_fixed_constraint(col, top)

# ========== 7. Create Load ==========
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass_kg  # Active by default

# ========== 8. Finalize Scene Settings ==========
# Ensure rigid body world is present
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
# Set gravity to Earth default (optional)
bpy.context.scene.rigidbody_world.gravity.z = -9.81

print("Structure built. All parts are passive rigid bodies with fixed constraints.")