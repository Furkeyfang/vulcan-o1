import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_size = (0.5, 0.5, 0.5)
base_loc = (0.0, 0.0, 0.25)
arm_size = (1.5, 0.2, 0.2)
arm_loc = (0.0, 0.0, 0.5)
tie_radius = 0.05
tie_length = 1.0
left_tie_start = (-0.75, 0.0, 0.5)
left_tie_end = (-0.75, 1.0, 0.5)
right_tie_start = (0.75, 0.0, 0.5)
right_tie_end = (0.75, 1.0, 0.5)
knuckle_radius = 0.1
knuckle_depth = 0.1
left_knuckle_loc = (-0.75, 1.0, 0.5)
right_knuckle_loc = (0.75, 1.0, 0.5)
motor_velocity = 2.0
simulation_frames = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create fixed base
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_size
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create steering arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_size
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'

# Fixed constraint between base and arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm_loc)
constraint_empty = bpy.context.active_object
constraint_empty.empty_display_size = 0.2
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = base
constraint.object2 = arm

# Create left tie rod (cylinder)
left_tie_mid = (
    (left_tie_start[0] + left_tie_end[0]) / 2,
    (left_tie_start[1] + left_tie_end[1]) / 2,
    (left_tie_start[2] + left_tie_end[2]) / 2
)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=tie_radius,
    depth=tie_length,
    location=left_tie_mid
)
left_tie = bpy.context.active_object
left_tie.rotation_euler = (math.radians(90), 0, 0)  # Orient along Y-axis
bpy.ops.rigidbody.object_add()
left_tie.rigid_body.type = 'ACTIVE'
left_tie.rigid_body.collision_shape = 'CONVEX_HULL'

# Create right tie rod
right_tie_mid = (
    (right_tie_start[0] + right_tie_end[0]) / 2,
    (right_tie_start[1] + right_tie_end[1]) / 2,
    (right_tie_start[2] + right_tie_end[2]) / 2
)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=tie_radius,
    depth=tie_length,
    location=right_tie_mid
)
right_tie = bpy.context.active_object
right_tie.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.rigidbody.object_add()
right_tie.rigid_body.type = 'ACTIVE'
right_tie.rigid_body.collision_shape = 'CONVEX_HULL'

# Create left knuckle (cylinder for wheel hub)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=knuckle_radius,
    depth=knuckle_depth,
    location=left_knuckle_loc
)
left_knuckle = bpy.context.active_object
left_knuckle.rotation_euler = (0, math.radians(90), 0)  # Orient along Y-axis
bpy.ops.rigidbody.object_add()
left_knuckle.rigid_body.type = 'ACTIVE'
left_knuckle.rigid_body.collision_shape = 'CONVEX_HULL'

# Create right knuckle
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=knuckle_radius,
    depth=knuckle_depth,
    location=right_knuckle_loc
)
right_knuckle = bpy.context.active_object
right_knuckle.rotation_euler = (0, math.radians(90), 0)
bpy.ops.rigidbody.object_add()
right_knuckle.rigid_body.type = 'ACTIVE'
right_knuckle.rigid_body.collision_shape = 'CONVEX_HULL'

# Hinge constraint: steering arm to left tie rod (Z-axis rotation)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=left_tie_start)
hinge1_empty = bpy.context.active_object
hinge1_empty.empty_display_size = 0.15
bpy.ops.rigidbody.constraint_add()
hinge1 = hinge1_empty.rigid_body_constraint
hinge1.type = 'HINGE'
hinge1.object1 = arm
hinge1.object2 = left_tie
hinge1.use_limit_z = True
hinge1.limit_z_lower = math.radians(-45)
hinge1.limit_z_upper = math.radians(45)

# Hinge constraint: steering arm to right tie rod
bpy.ops.object.empty_add(type='PLAIN_AXES', location=right_tie_start)
hinge2_empty = bpy.context.active_object
hinge2_empty.empty_display_size = 0.15
bpy.ops.rigidbody.constraint_add()
hinge2 = hinge2_empty.rigid_body_constraint
hinge2.type = 'HINGE'
hinge2.object1 = arm
hinge2.object2 = right_tie
hinge2.use_limit_z = True
hinge2.limit_z_lower = math.radians(-45)
hinge2.limit_z_upper = math.radians(45)

# Hinge constraint: left tie rod to left knuckle (Y-axis rotation)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=left_tie_end)
hinge3_empty = bpy.context.active_object
hinge3_empty.empty_display_size = 0.15
bpy.ops.rigidbody.constraint_add()
hinge3 = hinge3_empty.rigid_body_constraint
hinge3.type = 'HINGE'
hinge3.object1 = left_tie
hinge3.object2 = left_knuckle
hinge3.use_limit_y = True
hinge3.limit_y_lower = math.radians(-40)
hinge3.limit_y_upper = math.radians(40)

# Hinge constraint: right tie rod to right knuckle
bpy.ops.object.empty_add(type='PLAIN_AXES', location=right_tie_end)
hinge4_empty = bpy.context.active_object
hinge4_empty.empty_display_size = 0.15
bpy.ops.rigidbody.constraint_add()
hinge4 = hinge4_empty.rigid_body_constraint
hinge4.type = 'HINGE'
hinge4.object1 = right_tie
hinge4.object2 = right_knuckle
hinge4.use_limit_y = True
hinge4.limit_y_lower = math.radians(-40)
hinge4.limit_y_upper = math.radians(40)

# Motor constraint on steering arm rotation
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm_loc)
motor_empty = bpy.context.active_object
motor_empty.empty_display_size = 0.25
bpy.ops.rigidbody.constraint_add()
motor = motor_empty.rigid_body_constraint
motor.type = 'MOTOR'
motor.object1 = base
motor.object2 = arm
motor.use_angular_motor_z = True
motor.motor_angular_target_velocity_z = motor_velocity
motor.motor_angular_max_impulse_z = 10.0

# Set simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Steering linkage mechanism created successfully.")
print(f"Motor angular velocity: {motor_velocity} rad/s")
print(f"Simulation frames: {simulation_frames}")