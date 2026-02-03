import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.0)
arm_dim = (1.5, 0.3, 0.3)
arm_loc = (2.25, 0.0, 0.35)
hinge_pivot = (1.5, 0.0, 0.35)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 2.0
motor_torque = 100.0
frame_count = 100

# Create chassis (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'
chassis.rigid_body.collision_shape = 'BOX'

# Create steering arm (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Steering_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'

# Create hinge constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
hinge_empty.empty_display_size = 0.5

# Add rigid body constraint
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = chassis
constraint.object2 = arm
constraint.pivot_type = 'CUSTOM'

# Set constraint location and axis
constraint.pivot_x = hinge_pivot[0]
constraint.pivot_y = hinge_pivot[1]
constraint.pivot_z = hinge_pivot[2]
constraint.axis_x = hinge_axis[0]
constraint.axis_y = hinge_axis[1]
constraint.axis_z = hinge_axis[2]

# Configure motor
constraint.use_motor_angular = True
constraint.motor_angular_target_velocity = motor_velocity
constraint.motor_angular_max_impulse = motor_torque

# Set simulation parameters
bpy.context.scene.frame_end = frame_count
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Verification setup: Add driver to monitor rotation
# Create custom property to track arm rotation
arm["rotation_z"] = 0.0

# Add frame change handler to update rotation property
def update_rotation(scene):
    arm["rotation_z"] = abs(arm.rotation_euler.z)
    
# Register handler (commented for headless compatibility)
# bpy.app.handlers.frame_change_post.append(update_rotation)

print(f"Assembly created. Expected rotation after {frame_count} frames: {motor_velocity * frame_count / 60:.1f} rad = {motor_velocity * frame_count / 60 * 180 / 3.14159:.0f}°")
print("Hinge motor enabled with velocity:", motor_velocity, "rad/s")