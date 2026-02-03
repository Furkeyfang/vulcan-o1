import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
chassis_size = (3.0, 2.0, 0.5)
chassis_center = (0.0, 0.0, 0.5)
steering_arm_size = (1.5, 0.2, 0.3)
steering_arm_center = (0.0, 1.5, 0.9)
wheel_radius = 0.4
wheel_depth = 0.2
left_wheel_center = (0.75, 1.5, 0.9)
right_wheel_center = (-0.75, 1.5, 0.9)
pivot_point = (0.0, 1.5, 0.9)
motor_angular_velocity = 1.0
simulation_time = 0.5

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create chassis platform
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_center)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_size[0], chassis_size[1], chassis_size[2])
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'

# Create steering arm
bpy.ops.mesh.primitive_cube_add(size=1, location=steering_arm_center)
steering_arm = bpy.context.active_object
steering_arm.name = "SteeringArm"
steering_arm.scale = (steering_arm_size[0], steering_arm_size[1], steering_arm_size[2])
bpy.ops.rigidbody.object_add()
steering_arm.rigid_body.type = 'ACTIVE'

# Create left wheel (cylinder with axis along Y)
bpy.ops.mesh.primitive_cylinder_add(radius=wheel_radius, depth=wheel_depth, location=left_wheel_center)
left_wheel = bpy.context.active_object
left_wheel.name = "LeftWheel"
left_wheel.rotation_euler = (math.pi/2, 0, 0)  # Rotate 90° around X to align cylinder axis along Y
bpy.ops.rigidbody.object_add()
left_wheel.rigid_body.type = 'ACTIVE'

# Create right wheel
bpy.ops.mesh.primitive_cylinder_add(radius=wheel_radius, depth=wheel_depth, location=right_wheel_center)
right_wheel = bpy.context.active_object
right_wheel.name = "RightWheel"
right_wheel.rotation_euler = (math.pi/2, 0, 0)
bpy.ops.rigidbody.object_add()
right_wheel.rigid_body.type = 'ACTIVE'

# Create hinge constraint between chassis and steering arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_point)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = hinge_empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = chassis
constraint.object2 = steering_arm
constraint.pivot_type = 'CENTER'
# Align hinge axis to global Z
constraint.use_limits_angular = False
constraint.use_motor_angular = True
constraint.motor_angular_velocity = motor_angular_velocity
constraint.motor_angular_max_torque = 100.0  # High torque to ensure motion

# Create fixed constraint between steering arm and left wheel
bpy.ops.object.empty_add(type='PLAIN_AXES', location=left_wheel_center)
fixed_left_empty = bpy.context.active_object
fixed_left_empty.name = "Fixed_Left"
bpy.ops.rigidbody.constraint_add()
fixed_left = fixed_left_empty.rigid_body_constraint
fixed_left.type = 'FIXED'
fixed_left.object1 = steering_arm
fixed_left.object2 = left_wheel

# Create fixed constraint between steering arm and right wheel
bpy.ops.object.empty_add(type='PLAIN_AXES', location=right_wheel_center)
fixed_right_empty = bpy.context.active_object
fixed_right_empty.name = "Fixed_Right"
bpy.ops.rigidbody.constraint_add()
fixed_right = fixed_right_empty.rigid_body_constraint
fixed_right.type = 'FIXED'
fixed_right.object1 = steering_arm
fixed_right.object2 = right_wheel

# Configure simulation
bpy.context.scene.frame_end = int(simulation_time * 60)  # 60 fps
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容

# Verification setup: print initial and final rotation
print(f"Initial steering arm rotation: {steering_arm.rotation_euler.z}")
# In headless, we'd typically bake simulation here, but for data generation we just set up the scene