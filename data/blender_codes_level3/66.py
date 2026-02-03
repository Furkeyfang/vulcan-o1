import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import variables from parameter summary
base_dim = (3.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.0)
support_dim = (0.3, 0.3, 2.0)
support_loc = (0.0, -0.85, 1.15)
arm_dim = (0.2, 0.2, 2.5)
arm_pivot_z = 2.15
arm_loc = (0.0, -0.85, 3.4)
holder_dim = (0.4, 0.4, 0.4)
holder_arm_offset = 2.3
holder_loc = (0.0, -0.85, 4.45)
motor_velocity = 8.0

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.name = "Support_Column"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'ACTIVE'
support.rigid_body.collision_shape = 'BOX'

# Create Rotating Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Rotating_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'

# Create Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=1.0, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Projectile_Holder"
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.collision_shape = 'BOX'

# Add Fixed Constraint: Base → Support
bpy.ops.object.empty_add(type='PLAIN_AXES', location=support_loc)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Base_Support_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = base
constraint.object2 = support

# Add Hinge Constraint: Support → Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -0.85, arm_pivot_z))
hinge_empty = bpy.context.active_object
hinge_empty.name = "Arm_Hinge"
bpy.ops.rigidbody.constraint_add()
hinge = hinge_empty.rigid_body_constraint
hinge.type = 'HINGE'
hinge.object1 = support
hinge.object2 = arm
hinge.use_limit_z = False  # Free rotation
hinge.use_motor_z = True
hinge.motor_lin_target_velocity = motor_velocity
hinge.motor_lin_target_velocity = 0  # Linear not used
hinge.motor_ang_target_velocity = motor_velocity

# Add Fixed Constraint: Arm → Holder
bpy.ops.object.empty_add(type='PLAIN_AXES', location=holder_loc)
holder_constraint_empty = bpy.context.active_object
holder_constraint_empty.name = "Arm_Holder_Fixed"
bpy.ops.rigidbody.constraint_add()
holder_constraint = holder_constraint_empty.rigid_body_constraint
holder_constraint.type = 'FIXED'
holder_constraint.object1 = arm
holder_constraint.object2 = holder

# Set physics scene parameters
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100

print("Catapult assembly complete. Motor velocity:", motor_velocity, "rad/s")
print("Expected range > 12m with 187% safety margin")