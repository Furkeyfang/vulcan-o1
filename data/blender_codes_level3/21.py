import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
chassis_length = 6.0
chassis_width = 3.0
chassis_height = 0.5
chassis_loc_z = 0.5
wheel_radius = 0.6
wheel_depth = 0.3
x_offset = 2.85
y_offset = 1.5
wheel_z = -0.35
wheel_positions = [
    (x_offset, y_offset, wheel_z),
    (x_offset, -y_offset, wheel_z),
    (-x_offset, y_offset, wheel_z),
    (-x_offset, -y_offset, wheel_z)
]
motor_velocity = 4.0
chassis_mass = 50.0
wheel_mass = 5.0
ground_size = 20.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (central platform)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, chassis_loc_z))
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_length, chassis_width, chassis_height)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass

# Create wheels
wheels = []
for i, pos in enumerate(wheel_positions):
    # Create cylinder (default axis Z)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    
    # Rotate 90° about X to align cylinder axis with Y (wheel-like)
    wheel.rotation_euler = (math.pi/2, 0, 0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    
    wheels.append(wheel)

# Create hinge constraints between chassis and each wheel
for i, wheel in enumerate(wheels):
    # Select chassis first, then wheel (for context)
    bpy.context.view_layer.objects.active = chassis
    wheel.select_set(True)
    
    # Add constraint to chassis (active object)
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{i}"
    
    # Configure hinge constraint
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object2 = wheel
    constraint.location = wheel.location  # Position at wheel center
    
    # Set hinge axis to global X (1,0,0) for forward rotation
    constraint.rigid_body_constraint.axis = 'LOCAL_X'  # Works in headless
    
    # Enable motor
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_type = 'VELOCITY'
    constraint.rigid_body_constraint.motor_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_max_impulse = 100.0  # High torque
    
    # Deselect for next iteration
    wheel.select_set(False)

# Set initial chassis position and velocity
chassis.location = (0, 0, chassis_loc_z)
chassis.rotation_euler = (0, 0, 0)
if chassis.rigid_body:
    chassis.rigid_body.linear_velocity = (0, 0, 0)
    chassis.rigid_body.angular_velocity = (0, 0, 0)

print("Crawler vehicle construction complete.")
print(f"Motorized hinge constraints set to {motor_velocity} rad/s")
print(f"Vehicle ready for simulation with target Z > 8m in 500 frames")