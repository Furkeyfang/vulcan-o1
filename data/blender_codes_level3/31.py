import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define all parameters from summary
incline_length = 20.0
incline_width = 10.0
incline_thickness = 0.2
slope_angle_deg = 10.0
slope_angle_rad = math.radians(slope_angle_deg)

chassis_length = 3.0
chassis_width = 1.5
chassis_height = 0.4
wheel_radius = 0.4
wheel_depth = 0.15
motor_velocity = 2.0

rover_start_x = -3.0
cube_start_x = 0.0
cube_size = 0.8

# Calculated positions
incline_z_at_rover = rover_start_x * math.tan(slope_angle_rad)
wheel_z = incline_z_at_rover + wheel_radius * math.cos(slope_angle_rad)
chassis_z = incline_z_at_rover - (chassis_height/2) * math.cos(slope_angle_rad)
cube_z = (cube_size/2) * math.cos(slope_angle_rad)

wheel_x_offset = chassis_length/2 - wheel_radius
wheel_y_offset = chassis_width/2

# Create inclined plane
bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 0, 0))
incline = bpy.context.active_object
incline.name = "Incline"
incline.scale = (incline_length, incline_width, incline_thickness)
incline.rotation_euler = (0, slope_angle_rad, 0)
# Move so top surface starts at Z=0 at X=0
incline.location.x = incline_length/2 * math.cos(slope_angle_rad) - incline_thickness/2 * math.sin(slope_angle_rad)
incline.location.z = incline_length/2 * math.sin(slope_angle_rad) + incline_thickness/2 * math.cos(slope_angle_rad)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
incline.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=(rover_start_x, 0, chassis_z))
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_length, chassis_width, chassis_height)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'

# Create four wheels
wheel_positions = [
    (rover_start_x + wheel_x_offset, wheel_y_offset, wheel_z),
    (rover_start_x + wheel_x_offset, -wheel_y_offset, wheel_z),
    (rover_start_x - wheel_x_offset, wheel_y_offset, wheel_z),
    (rover_start_x - wheel_x_offset, -wheel_y_offset, wheel_z)
]

wheels = []
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos,
        rotation=(0, 0, math.radians(90))
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    wheels.append(wheel)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'

# Add hinge constraints between wheels and chassis
for wheel in wheels:
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel.name}"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_velocity = motor_velocity
    # Hinge axis is local X (cylinder's axis)
    constraint.rigid_body_constraint.axis = 'LOCAL_X'

# Create cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(cube_start_x, 0, cube_z))
cube = bpy.context.active_object
cube.name = "Cube"
cube.scale = (cube_size, cube_size, cube_size)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Adjust masses for realistic behavior
chassis.rigid_body.mass = 20.0
for wheel in wheels:
    wheel.rigid_body.mass = 2.0
cube.rigid_body.mass = 5.0

# Set friction coefficients for better traction
for wheel in wheels:
    wheel.rigid_body.friction = 1.0
    wheel.rigid_body.use_margin = True
    wheel.rigid_body.collision_margin = 0.0

# Set scene gravity (default is -9.81 Z)
bpy.context.scene.use_gravity = True

# Optional: Set simulation end frame
bpy.context.scene.frame_end = 500

print("Rover construction complete. Simulation ready.")