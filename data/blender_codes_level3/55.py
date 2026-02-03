import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (-0.5, 0.0, -2.2)
support_dim = (0.2, 0.2, 2.5)
support_loc = (-2.0, 0.0, -0.95)
arm_dim = (0.15, 0.15, 2.0)
arm_loc = (-1.0, 0.0, 0.3)
holder_dim = (0.3, 0.3, 0.3)
holder_loc = (0.0, 0.0, 0.3)
hinge_pivot = (-1.5, 0.0, 0.3)
motor_velocity = 7.0
frame_end = 150

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# 1. Base Platform
bpy.ops.mesh.primitive_cube_add(size=2.0, location=base_loc)
base = bpy.context.active_object
base.scale = (base_dim[0]/2.0, base_dim[1]/2.0, base_dim[2]/2.0)
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. Support Arm
bpy.ops.mesh.primitive_cube_add(size=2.0, location=support_loc)
support = bpy.context.active_object
support.scale = (support_dim[0]/2.0, support_dim[1]/2.0, support_dim[2]/2.0)
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'

# 3. Throwing Arm
bpy.ops.mesh.primitive_cube_add(size=2.0, location=arm_loc)
arm = bpy.context.active_object
arm.scale = (arm_dim[0]/2.0, arm_dim[1]/2.0, arm_dim[2]/2.0)
# Rotate 90° around Y to align length along X-axis
arm.rotation_euler = (0.0, math.radians(90.0), 0.0)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# 4. Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=2.0, location=holder_loc)
holder = bpy.context.active_object
holder.scale = (holder_dim[0]/2.0, holder_dim[1]/2.0, holder_dim[2]/2.0)
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'

# 5. Fixed Constraints
# Base to World (empty as ground anchor)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.constraint_add()
constraint_base = bpy.context.active_object
constraint_base.constraint.type = 'FIXED'
constraint_base.constraint.object1 = base
constraint_base.constraint.object2 = ground

# Support to Base
bpy.ops.rigidbody.constraint_add()
constraint_support = bpy.context.active_object
constraint_support.constraint.type = 'FIXED'
constraint_support.constraint.object1 = support
constraint_support.constraint.object2 = base

# Holder to Arm
bpy.ops.rigidbody.constraint_add()
constraint_holder = bpy.context.active_object
constraint_holder.constraint.type = 'FIXED'
constraint_holder.constraint.object1 = holder
constraint_holder.constraint.object2 = arm

# 6. Hinge Constraint with Motor
bpy.ops.rigidbody.constraint_add()
constraint_hinge = bpy.context.active_object
constraint_hinge.constraint.type = 'HINGE'
constraint_hinge.constraint.object1 = support
constraint_hinge.constraint.object2 = arm
constraint_hinge.constraint.pivot_type = 'CUSTOM'
constraint_hinge.constraint.use_override_solver_iterations = True
constraint_hinge.constraint.solver_iterations = 50
# Set pivot at hinge point in world coordinates
constraint_hinge.location = hinge_pivot
# Align hinge axis to global Y
constraint_hinge.rotation_euler = (0.0, 0.0, 0.0)
constraint_hinge.constraint.use_motor = True
constraint_hinge.constraint.motor_angular_target_velocity = motor_velocity
constraint_hinge.constraint.use_limit_angular = False

# 7. Simulation settings
bpy.context.scene.frame_end = frame_end