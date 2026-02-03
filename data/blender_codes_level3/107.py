import bpy

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from summary
chassis_dim = (3.0, 2.0, 0.5)
chassis_loc = (0.0, 0.0, 0.5)
steering_arm_dim = (0.5, 1.5, 0.3)
steering_arm_loc = (0.0, 0.75, 0.9)
hinge_pivot = (0.0, 0.75, 0.75)
hinge_axis = (0.0, 0.0, 1.0)
motor_target_velocity = 0.35

# Create Chassis (Passive Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'

# Create Steering Arm (Active Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=steering_arm_loc)
steering_arm = bpy.context.active_object
steering_arm.scale = steering_arm_dim
bpy.ops.rigidbody.object_add()
# Default type is 'ACTIVE', so no need to change

# Create Empty for Hinge Constraint at Pivot
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
constraint_empty = bpy.context.active_object

# Add Rigid Body Constraint to Empty
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'HINGE'

# Link Constraint to Chassis and Steering Arm
constraint.object1 = chassis
constraint.object2 = steering_arm

# Set Hinge Axis (in world coordinates)
constraint.axis = hinge_axis

# Configure Motor
constraint.use_motor = True
constraint.motor_type = 'VELOCITY'
constraint.motor_velocity = motor_target_velocity

# Set simulation range for verification (optional, for rendering)
bpy.context.scene.frame_end = 100