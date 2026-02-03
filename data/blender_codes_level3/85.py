import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 2.0, 0.4)
chassis_loc = (0.0, 0.0, 0.4)
wheel_radius = 0.3
wheel_depth = 0.15
left_y = -1.0
right_y = 1.0
front_x = 1.5
rear_x = -1.5
wheel_center_z = 0.3
front_left_loc = (front_x, left_y, wheel_center_z)
rear_left_loc = (rear_x, left_y, wheel_center_z)
front_right_loc = (front_x, right_y, wheel_center_z)
rear_right_loc = (rear_x, right_y, wheel_center_z)
motor_speed_fr = 2.0
motor_speed_rr = -2.0
chassis_mass = 10.0
wheel_mass = 1.0

# Create chassis (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass

# Function to create a wheel (cylinder) with proper orientation
def create_wheel(location, name):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° around Y to align cylinder axis with X (hinge axis)
    wheel.rotation_euler = (0, math.pi/2, 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    return wheel

# Create wheels
wheel_fl = create_wheel(front_left_loc, "Wheel_FL")
wheel_rl = create_wheel(rear_left_loc, "Wheel_RL")
wheel_fr = create_wheel(front_right_loc, "Wheel_FR")
wheel_rr = create_wheel(rear_right_loc, "Wheel_RR")

# Add constraints for left wheels (Fixed)
def add_fixed_constraint(obj, target):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.constraint_add()
    constraint = obj.rigid_body_constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = target

add_fixed_constraint(wheel_fl, chassis)
add_fixed_constraint(wheel_rl, chassis)

# Add constraints for right wheels (Hinge with motor)
def add_hinge_constraint(obj, target, motor_speed):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.constraint_add()
    constraint = obj.rigid_body_constraints[-1]
    constraint.type = 'HINGE'
    constraint.object1 = target
    # Set axis in world coordinates (X-axis for rotation)
    constraint.axis = 'LOCAL_X'  # Hinge axis along local X of constraint object
    constraint.use_motor = True
    constraint.motor_angular_velocity = motor_speed

add_hinge_constraint(wheel_fr, chassis, motor_speed_fr)
add_hinge_constraint(wheel_rr, chassis, motor_speed_rr)

# Set up physics world (optional, ensure gravity)
bpy.context.scene.gravity = (0, 0, -9.81)

# Ensure all objects are visible and collision bounds are set
for obj in bpy.context.scene.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_shape = 'MESH'

print("Skid-steering robot created successfully.")