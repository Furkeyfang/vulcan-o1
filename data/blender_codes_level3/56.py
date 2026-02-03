import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
support_dim = (0.3, 0.3, 2.5)
support_loc = (0.0, -1.35, 1.75)
pivot_loc = (0.0, -1.35, 3.0)
arm_dim = (0.2, 2.0, 0.2)
arm_loc = (0.0, -0.35, 3.0)
projectile_dim = (0.5, 0.5, 0.5)
projectile_loc = (0.0, 0.65, 3.0)
hinge_axis = (0.0, 1.0, 0.0)
motor_velocity = 3.0
constraint_break_threshold = 10.0

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# 1. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.name = "Support"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'

# 3. Create Catapult Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 5.0  # Moderate mass

# 4. Create Projectile
bpy.ops.mesh.primitive_cube_add(size=1.0, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = projectile_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = 20.0  # Heavy projectile

# 5. Add Constraints
# Base-Support Fixed Constraint
bpy.ops.rigidbody.constraint_add()
constraint_base_support = bpy.context.active_object
constraint_base_support.name = "Base_Support_Fixed"
constraint_base_support.rigid_body_constraint.type = 'FIXED'
constraint_base_support.rigid_body_constraint.object1 = base
constraint_base_support.rigid_body_constraint.object2 = support
constraint_base_support.location = support_loc

# Support-Arm Hinge Constraint (with motor)
bpy.ops.rigidbody.constraint_add()
constraint_hinge = bpy.context.active_object
constraint_hinge.name = "Support_Arm_Hinge"
constraint_hinge.rigid_body_constraint.type = 'HINGE'
constraint_hinge.rigid_body_constraint.object1 = support
constraint_hinge.rigid_body_constraint.object2 = arm
constraint_hinge.location = pivot_loc
constraint_hinge.rigid_body_constraint.use_limit_z = False
constraint_hinge.rigid_body_constraint.use_motor_z = True
constraint_hinge.rigid_body_constraint.motor_lin_target_velocity = motor_velocity
constraint_hinge.rigid_body_constraint.motor_lin_servo_target_velocity = motor_velocity

# Arm-Projectile Temporary Fixed Constraint (breaks on launch)
bpy.ops.rigidbody.constraint_add()
constraint_temp = bpy.context.active_object
constraint_temp.name = "Arm_Projectile_Temp"
constraint_temp.rigid_body_constraint.type = 'FIXED'
constraint_temp.rigid_body_constraint.object1 = arm
constraint_temp.rigid_body_constraint.object2 = projectile
constraint_temp.location = projectile_loc
constraint_temp.rigid_body_constraint.use_breaking = True
constraint_temp.rigid_body_constraint.breaking_threshold = constraint_break_threshold

# Set initial rotation of arm to horizontal (rest position)
arm.rotation_euler = (0.0, 0.0, 0.0)

# Ensure all objects are visible for simulation
for obj in [base, support, arm, projectile]:
    obj.hide_render = False
    obj.hide_viewport = False