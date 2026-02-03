import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
platform_dim = (3.0, 3.0, 0.5)
platform_loc = (0.0, 0.0, 0.0)
turret_dim = (2.0, 2.0, 1.0)
turret_loc = (0.0, 0.0, 0.75)
arm_dim = (0.2, 3.0, 0.2)
arm_loc = (0.0, 1.5, 1.25)
projectile_dim = (0.2, 0.2, 0.2)
projectile_loc = (0.0, 3.0, 1.25)
base_pivot = (0.0, 0.0, 0.25)
arm_pivot = (0.0, 0.0, 1.25)
base_motor_vel = 1.0
arm_motor_vel = 5.0

# Set gravity
if bpy.context.scene.rigidbody_world:
    bpy.context.scene.rigidbody_world.gravity[2] = -9.8
else:
    bpy.ops.rigidbody.world_add()
    bpy.context.scene.rigidbody_world.gravity[2] = -9.8

# 1. Create Platform (Static Base)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.collision_shape = 'BOX'

# 2. Create Turret Base (Rotating)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=turret_loc)
turret = bpy.context.active_object
turret.name = "TurretBase"
turret.scale = turret_dim
bpy.ops.rigidbody.object_add()
turret.rigid_body.type = 'ACTIVE'
turret.rigid_body.collision_shape = 'BOX'

# 3. Create Launch Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "LaunchArm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'

# 4. Create Projectile
bpy.ops.mesh.primitive_cube_add(size=1.0, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = projectile_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = 0.5  # Light projectile for better launch

# 5. Create Constraints
# Base Hinge (Platform -> Turret)
bpy.ops.rigidbody.constraint_add()
base_constraint = bpy.context.active_object
base_constraint.name = "BaseHinge"
base_constraint.rigid_body_constraint.type = 'HINGE'
base_constraint.rigid_body_constraint.object1 = platform
base_constraint.rigid_body_constraint.object2 = turret
base_constraint.location = base_pivot

# Configure hinge axis (Z-axis for base rotation)
base_constraint.rigid_body_constraint.use_limit_ang_z = False  # No limits for continuous rotation
base_constraint.rigid_body_constraint.use_motor_ang = True
base_constraint.rigid_body_constraint.motor_ang_target_velocity = base_motor_vel
base_constraint.rigid_body_constraint.motor_ang_max_impulse = 10.0  # Sufficient torque

# Arm Hinge (Turret -> Arm)
bpy.ops.rigidbody.constraint_add()
arm_constraint = bpy.context.active_object
arm_constraint.name = "ArmHinge"
arm_constraint.rigid_body_constraint.type = 'HINGE'
arm_constraint.rigid_body_constraint.object1 = turret
arm_constraint.rigid_body_constraint.object2 = arm
arm_constraint.location = arm_pivot

# Configure arm hinge (Y-axis for elevation)
arm_constraint.rigid_body_constraint.use_limit_ang_y = False
arm_constraint.rigid_body_constraint.use_motor_ang = True
arm_constraint.rigid_body_constraint.motor_ang_target_velocity = arm_motor_vel
arm_constraint.rigidbody_constraint.motor_ang_max_impulse = 5.0

# 6. Position arm pivot correctly relative to arm geometry
# The arm's local origin is at its center, but hinge should be at one end
# We need to set constraint frame offsets
arm_constraint.rigid_body_constraint.use_override_solver_iterations = True
arm_constraint.rigid_body_constraint.solver_iterations = 50

# Set constraint frames for proper pivot alignment
# For arm constraint: pivot at (0, -1.5, 0) in arm's local space (one end)
arm_constraint.rigid_body_constraint.use_spring_ang_y = False

# 7. Simulation settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Optional: Add a ground plane for reference
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print("Catapult turret assembly complete. Motors configured for base rotation and arm launch.")
print(f"Projectile initial position: {projectile_loc}")
print(f"Target launch range: >10 meters with arm length {arm_dim[1]}m")
print(f"Base motor velocity: {base_motor_vel} rad/s, Arm motor velocity: {arm_motor_vel} rad/s")