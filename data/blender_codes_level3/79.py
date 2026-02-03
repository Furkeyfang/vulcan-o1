import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.4)
wheel_radius = 0.3
wheel_depth = 0.15
front_wheel_x = -1.2
rear_wheel_x = 1.2
wheel_y_offset = 0.75
wheel_z = 0.3
steering_motor_velocity = 0.0
steering_motor_max_torque = 10.0
chassis_mass = 10.0
wheel_mass = 2.5

# Create chassis (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.collision_shape = 'BOX'

# Wheel creation function
def create_wheel(name, location):
    # Cylinder aligned along Y-axis for rolling
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° around X to align cylinder axis with Y (rolling axis)
    wheel.rotation_euler = (mathutils.radians(90), 0, 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.collision_shape = 'CONE'  # Approximation for cylinder
    return wheel

# Create four wheels
wheels = {
    "front_left": create_wheel("Wheel_FL", (front_wheel_x, -wheel_y_offset, wheel_z)),
    "front_right": create_wheel("Wheel_FR", (front_wheel_x, wheel_y_offset, wheel_z)),
    "rear_left": create_wheel("Wheel_RL", (rear_wheel_x, -wheel_y_offset, wheel_z)),
    "rear_right": create_wheel("Wheel_RR", (rear_wheel_x, wheel_y_offset, wheel_z))
}

# Constraint creation function
def add_hinge_constraint(name, obj_a, obj_b, location, axis, use_motor=False, motor_vel=0.0, max_torque=10.0):
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    pivot = bpy.context.active_object
    pivot.name = name
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = pivot.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    # Set axis in world coordinates (since empties are at wheel centers)
    if axis == 'Y':
        constraint.use_angular_x = False
        constraint.use_angular_y = True
        constraint.use_angular_z = False
    elif axis == 'Z':
        constraint.use_angular_x = False
        constraint.use_angular_y = False
        constraint.use_angular_z = True
    # Motor settings for steering hinges
    if use_motor:
        constraint.use_motor = True
        constraint.motor_angular_target_velocity = motor_vel
        constraint.motor_max_impulse = max_torque

# Add rolling hinges (Y-axis) for all wheels
for wheel_name, wheel_obj in wheels.items():
    add_hinge_constraint(
        f"{wheel_name}_Roll",
        chassis, wheel_obj,
        wheel_obj.location,
        axis='Y',
        use_motor=False
    )

# Add steering hinges (Z-axis) only for rear wheels
for wheel_name in ["rear_left", "rear_right"]:
    wheel_obj = wheels[wheel_name]
    add_hinge_constraint(
        f"{wheel_name}_Steer",
        chassis, wheel_obj,
        wheel_obj.location,
        axis='Z',
        use_motor=True,
        motor_vel=steering_motor_velocity,
        max_torque=steering_motor_max_torque
    )

# Set world gravity (default -9.81 Z is fine)
bpy.context.scene.gravity = (0, 0, -9.81)

# Verification: Activate steering motors to turn right
# This would be done in simulation by changing motor_angular_target_velocity
# Example: set to 1.0 rad/s for both rear wheels
print("Robot constructed. To steer right, set rear steering hinge motors to positive angular velocity.")