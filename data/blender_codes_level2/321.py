import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
col_dim_x = 0.5
col_dim_y = 0.5
col_height = 10.0
col_loc = (0.0, 0.0, 5.0)
tread_cnt = 10
tread_len = 2.0
tread_dep = 0.8
tread_thk = 0.1
tread_y_off = 0.65
tread_start_z = 0.5
vert_spacing = 1.0
load_mass = 120.0
load_dim = 0.3
load_z_off = 0.2
con_pivot_y = 0.25

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create vertical support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_dim_x, col_dim_y, col_height)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create stair treads and constraints
for i in range(tread_cnt):
    tread_z = tread_start_z + i * vert_spacing
    tread_loc = (0.0, tread_y_off, tread_z)
    
    # Tread object
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tread_loc)
    tread = bpy.context.active_object
    tread.name = f"Tread_{i:02d}"
    tread.scale = (tread_len, tread_dep, tread_thk)
    bpy.ops.rigidbody.object_add()
    tread.rigid_body.type = 'ACTIVE'
    tread.rigid_body.collision_shape = 'BOX'
    
    # Fixed constraint at inner edge of tread
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_Constraint_{i:02d}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = column
    constraint.rigid_body_constraint.object2 = tread
    # Set constraint pivot at column surface (inner edge of tread)
    constraint.location = (0.0, con_pivot_y, tread_z)
    
    # Load block on tread
    load_loc = (0.0, tread_y_off, tread_z + load_z_off)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
    load = bpy.context.active_object
    load.name = f"Load_{i:02d}"
    load.scale = (load_dim, load_dim, load_dim)
    bpy.ops.rigidbody.object_add()
    load.rigid_body.type = 'ACTIVE'
    load.rigid_body.mass = load_mass
    load.rigid_body.collision_shape = 'BOX'

# Set gravity to standard -9.81 m/s² in Z
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)