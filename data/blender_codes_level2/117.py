import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
column_dim = (0.5, 0.5, 3.0)
column_loc = (0.0, 0.0, 1.5)
arm_dim = (2.0, 0.3, 0.3)
arm_loc = (1.0, 0.0, 3.0)
platform_dim = (0.8, 0.8, 0.1)
platform_loc = (2.0, 0.0, 3.2)
load_mass_kg = 300.0
load_dim = (0.5, 0.5, 0.5)
load_loc = (2.0, 0.0, 3.5)
hinge_motor_target_velocity = 0.0
hinge_motor_max_torque = 10000.0
simulation_frames = 500
gravity_z = -9.8

# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, gravity_z)
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 1. Create Vertical Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.friction = 1.0
column.rigid_body.restitution = 0.0

# 2. Create Cantilever Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 50.0  # Estimated arm mass
arm.rigid_body.friction = 1.0

# 3. Create Load Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.friction = 1.0

# 4. Create 300kg Load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass_kg
load.rigid_body.friction = 1.0

# 5. Create Hinge Constraint between Column and Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 3.0))
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = hinge_empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = column
constraint.object2 = arm
# Hinge axis local to arm: Y-axis rotation
constraint.use_limit_angle = True
constraint.limit_angle_min = 0.0
constraint.limit_angle_max = 0.0  # Locked initially
constraint.use_motor_angular = True
constraint.motor_angular_target_velocity = hinge_motor_target_velocity
constraint.motor_angular_max_torque = hinge_motor_max_torque

# 6. Create Fixed Constraint between Arm and Platform
bpy.ops.object.empty_add(type='PLAIN_AXES', location=platform_loc)
fixed_empty = bpy.context.active_object
fixed_empty.name = "Arm_Platform_Fixed"
bpy.ops.rigidbody.constraint_add()
fixed_constraint = fixed_empty.rigid_body_constraint
fixed_constraint.type = 'FIXED'
fixed_constraint.object1 = arm
fixed_constraint.object2 = platform

# 7. Add deflection marker (non-rendering) for verification
bpy.ops.mesh.primitive_cube_add(size=0.05, location=platform_loc)
marker = bpy.context.active_object
marker.name = "Deflection_Marker"
marker.hide_render = True
marker.hide_viewport = False

# 8. Set simulation end frame
bpy.context.scene.frame_end = simulation_frames

# Optional: Bake simulation for consistent results
bpy.ops.ptcache.bake_all(bake=True)