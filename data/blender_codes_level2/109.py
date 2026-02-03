import bpy
import mathutils

# Clear existing
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_dim = column_dim = (0.4, 0.4, 2.5)
col_loc = column_loc = (0.0, 0.0, 1.25)
bm_dim = beam_dim = (3.0, 0.3, 0.3)
bm_loc = beam_loc = (0.7, 0.0, 2.65)
plat_dim = platform_dim = (2.0, 1.5, 0.05)
plat_loc = platform_loc = (2.2, 0.0, 2.825)
force_mag = force_magnitude
steel_rho = steel_density
con_stiff = constraint_stiffness

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 1. Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.scale = (col_dim[0]/2.0, col_dim[1]/2.0, col_dim[2]/2.0)  # cube default 2x2x2
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.mass = steel_rho * (col_dim[0]*col_dim[1]*col_dim[2])
column.rigid_body.collision_shape = 'BOX'

# 2. Beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=bm_loc)
beam = bpy.context.active_object
beam.scale = (bm_dim[0]/2.0, bm_dim[1]/2.0, bm_dim[2]/2.0)
beam.name = "Beam"
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = steel_rho * (bm_dim[0]*bm_dim[1]*bm_dim[2])
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.linear_damping = 0.5
beam.rigid_body.angular_damping = 0.5

# 3. Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plat_loc)
platform = bpy.context.active_object
platform.scale = (plat_dim[0]/2.0, plat_dim[1]/2.0, plat_dim[2]/2.0)
platform.name = "Platform"
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = steel_rho * (plat_dim[0]*plat_dim[1]*plat_dim[2])
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.linear_damping = 0.5

# Apply downward force as constant force on platform
platform.rigid_body.constant_force = (0.0, 0.0, -force_mag)

# 4. Fixed Constraints
def add_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = 0.2
    # Set as rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2
    empty.rigid_body_constraint.use_breaking = True
    empty.rigid_body_constraint.breaking_threshold = force_mag * 5.0
    empty.rigid_body_constraint.use_limit_lin_x = True
    empty.rigid_body_constraint.use_limit_lin_y = True
    empty.rigid_body_constraint.use_limit_lin_z = True
    empty.rigid_body_constraint.limit_lin_x_lower = -0.001
    empty.rigid_body_constraint.limit_lin_x_upper = 0.001
    empty.rigid_body_constraint.limit_lin_y_lower = -0.001
    empty.rigid_body_constraint.limit_lin_y_upper = 0.001
    empty.rigid_body_constraint.limit_lin_z_lower = -0.001
    empty.rigid_body_constraint.limit_lin_z_upper = 0.001
    empty.rigid_body_constraint.stiffness = con_stiff
    return empty

# Column-Beam constraint placed at connection point (X=0.2, Z=2.5)
con1_loc = (0.2, 0.0, 2.5)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=con1_loc)
con1 = bpy.context.active_object
con1.name = "Constraint_Column_Beam"
bpy.ops.rigidbody.constraint_add()
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = column
con1.rigid_body_constraint.object2 = beam
con1.rigid_body_constraint.stiffness = con_stiff

# Beam-Platform constraint at free end (X=2.2, Z=2.65)
con2_loc = (2.2, 0.0, 2.65)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=con2_loc)
con2 = bpy.context.active_object
con2.name = "Constraint_Beam_Platform"
bpy.ops.rigidbody.constraint_add()
con2.rigid_body_constraint.type = 'FIXED'
con2.rigid_body_constraint.object1 = beam
con2.rigid_body_constraint.object2 = platform
con2.rigid_body_constraint.stiffness = con_stiff

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = sim_frames

# Bake rigid body simulation
bpy.ops.ptcache.bake_all(bake=True)

# Verification: measure platform Z displacement at frame 100
bpy.context.scene.frame_set(sim_frames)
deflection = plat_loc[2] - platform.location.z
print(f"Final platform Z: {platform.location.z}")
print(f"Deflection: {deflection:.4f} m")
print(f"Allowable: {max_allowed_deflection} m")
print(f"Pass: {abs(deflection) < max_allowed_deflection}")