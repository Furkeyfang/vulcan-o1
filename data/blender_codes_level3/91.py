import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
chassis_dim = (2.0, 1.0, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
column_rad = 0.05
column_ht = 0.4
column_loc = (1.0, 0.0, 0.5)
arm_dim = (0.6, 0.1, 0.1)
arm_loc = (1.0, 0.0, 0.75)
wheel_rad = 0.25
wheel_depth = 0.1
wheel_left_loc = (0.7, 0.0, 0.45)
wheel_right_loc = (1.3, 0.0, 0.45)
initial_velocity = (2.0, 0.0, 0.0)
motor_velocity = 2.0
ground_size = (10.0, 10.0, 0.2)
ground_loc = (0.0, 0.0, -0.1)

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.linear_velocity = initial_velocity

# Create steering column
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=column_rad,
    depth=column_ht,
    location=column_loc
)
column = bpy.context.active_object
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Fixed constraint: chassis to column
bpy.ops.rigidbody.constraint_add()
constraint_fixed = bpy.context.active_object
constraint_fixed.rigid_body_constraint.type = 'FIXED'
constraint_fixed.rigid_body_constraint.object1 = chassis
constraint_fixed.rigid_body_constraint.object2 = column

# Create steering arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Hinge constraint: column to arm (Z-axis rotation, motorized)
bpy.ops.rigidbody.constraint_add()
constraint_steer = bpy.context.active_object
constraint_steer.rigid_body_constraint.type = 'HINGE'
constraint_steer.rigid_body_constraint.object1 = column
constraint_steer.rigid_body_constraint.object2 = arm
constraint_steer.rigid_body_constraint.use_motor = True
constraint_steer.rigid_body_constraint.motor_angular_target_velocity = motor_velocity
constraint_steer.rigid_body_constraint.use_limit_angular = False
# Align hinge axis to global Z
constraint_steer.rotation_euler = (0, 0, 0)

# Create left wheel
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_rad,
    depth=wheel_depth,
    location=wheel_left_loc
)
wheel_left = bpy.context.active_object
wheel_left.rotation_euler = (0, math.pi/2, 0)  # Rotate for X-axis hinge
bpy.ops.rigidbody.object_add()
wheel_left.rigid_body.type = 'ACTIVE'

# Hinge constraint: arm to left wheel (X-axis rotation)
bpy.ops.rigidbody.constraint_add()
constraint_wheel_left = bpy.context.active_object
constraint_wheel_left.rigid_body_constraint.type = 'HINGE'
constraint_wheel_left.rigid_body_constraint.object1 = arm
constraint_wheel_left.rigid_body_constraint.object2 = wheel_left
constraint_wheel_left.rigid_body_constraint.use_limit_angular = False
# Align hinge axis to global X (wheel's local rotation axis after 90° Y rotation)
constraint_wheel_left.rotation_euler = (0, 0, 0)

# Create right wheel
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_rad,
    depth=wheel_depth,
    location=wheel_right_loc
)
wheel_right = bpy.context.active_object
wheel_right.rotation_euler = (0, math.pi/2, 0)
bpy.ops.rigidbody.object_add()
wheel_right.rigid_body.type = 'ACTIVE'

# Hinge constraint: arm to right wheel (X-axis rotation)
bpy.ops.rigidbody.constraint_add()
constraint_wheel_right = bpy.context.active_object
constraint_wheel_right.rigid_body_constraint.type = 'HINGE'
constraint_wheel_right.rigid_body_constraint.object1 = arm
constraint_wheel_right.rigid_body_constraint.object2 = wheel_right
constraint_wheel_right.rigid_body_constraint.use_limit_angular = False
constraint_wheel_right.rotation_euler = (0, 0, 0)

# Ensure all constraints are in same collection
for obj in [constraint_fixed, constraint_steer, constraint_wheel_left, constraint_wheel_right]:
    obj.hide_render = True
    obj.hide_viewport = True

# Set simulation settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100