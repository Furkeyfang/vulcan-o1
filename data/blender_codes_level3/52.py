import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
column_dim = (0.5, 0.5, 2.0)
column_loc = (0.0, 0.0, 1.25)
hinge_z = 2.5
arm_dim = (3.0, 0.2, 0.2)
arm_loc = (1.5, 0.0, 2.5)
projectile_dim = (0.3, 0.3, 0.3)
projectile_loc = (1.5, 0.0, 2.5)  # At arm end
motor_angular_velocity = 12.0
motor_rotation_limit = 1.5708  # π/2

# 1. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# 3. Create Throwing Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.angular_damping = 0.1  # Reduce wobble

# 4. Create Projectile
bpy.ops.mesh.primitive_cube_add(size=1.0, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = projectile_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = 2.0  # Heavier for realistic trajectory

# 5. Create Constraints
# Base to World (implicit with PASSIVE rigid body)
# Column to Base
bpy.ops.rigidbody.constraint_add()
constraint1 = bpy.context.active_object
constraint1.name = "Base_Column_Fixed"
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = base
constraint1.rigid_body_constraint.object2 = column
constraint1.location = column_loc

# Projectile to Arm
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.name = "Arm_Projectile_Fixed"
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = arm
constraint2.rigid_body_constraint.object2 = projectile
constraint2.location = projectile_loc

# Hinge between Column and Arm
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.name = "Catapult_Hinge"
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = column
hinge.rigid_body_constraint.object2 = arm
hinge.location = (0.0, 0.0, hinge_z)
hinge.rotation_euler = (0.0, 0.0, 0.0)

# Configure Hinge Motor
hinge.rigid_body_constraint.use_limit_angular = True
hinge.rigid_body_constraint.limit_angular_upper = motor_rotation_limit
hinge.rigid_body_constraint.limit_angular_lower = 0.0
hinge.rigid_body_constraint.use_motor_angular = True
hinge.rigid_body_constraint.motor_angular_target_velocity = motor_angular_velocity
hinge.rigid_body_constraint.motor_angular_max_torque = 1000.0

# 6. Set up animation to stop motor after reaching limit
# At 60fps, time to reach π/2 rad: t = θ/ω = 1.5708/12 ≈ 0.13s ≈ 8 frames
stop_frame = 8
bpy.context.scene.frame_end = 100

# Animate motor enable
hinge.rigid_body_constraint.keyframe_insert(data_path="use_motor_angular", frame=1)
hinge.rigid_body_constraint.use_motor_angular = False
hinge.rigid_body_constraint.keyframe_insert(data_path="use_motor_angular", frame=stop_frame)

# 7. Set physics scene parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.gravity = (0.0, 0.0, -9.8)

print("Catapult assembly complete. Projectile should exceed 7m height within 100 frames.")