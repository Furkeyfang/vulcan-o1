import bpy
import math

# ===== CLEAR SCENE =====
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ===== PARAMETERS =====
# Platform
platform_dim = (3.0, 2.0, 0.5)
platform_loc_slope = (2.0, 0.0, 0.25)

# Wheels
wheel_radius = 0.4
wheel_depth = 0.2
# Wheel offsets from platform center (before adding platform location)
wheel_offsets = [
    (1.5, 1.0, 0.4),
    (1.5, -1.0, 0.4),
    (-1.5, 1.0, 0.4),
    (-1.5, -1.0, 0.4)
]

# Motors
motor_velocity = 4.0

# Slope
slope_start_x = 2.0
slope_length = 10.0
slope_width = 4.0
slope_height = 3.0
slope_angle = math.atan(slope_height / slope_length)  # ~16.7 degrees

# ===== CREATE SLOPE =====
# Create plane and scale to ramp dimensions
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0,0,0))
slope = bpy.context.active_object
slope.name = "Slope"
slope.scale = (slope_length, slope_width, 1.0)

# Position and rotate: start at (slope_start_x, 0, 0)
# Center of plane after scaling: (slope_length/2, 0, 0) in local coordinates
# We want left edge at X=slope_start_x, so translate by:
# X = slope_start_x + slope_length/2
# Z = 0 (base) but rotated will lift one edge
slope.location.x = slope_start_x + slope_length/2
slope.location.z = 0.0

# Rotate around Y-axis: positive rotation lifts far end
slope.rotation_euler = (0.0, slope_angle, 0.0)

# Convert to rigid body (passive - static)
bpy.ops.rigidbody.object_add()
slope.rigid_body.type = 'PASSIVE'

# ===== CREATE CHASSIS PLATFORM =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc_slope)
platform = bpy.context.active_object
platform.name = "Chassis_Platform"
platform.scale = platform_dim

# Add rigid body (passive - moves but not by physics)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'

# ===== CREATE WHEELS =====
wheels = []
for i, offset in enumerate(wheel_offsets):
    # Calculate world position
    wheel_pos = (
        platform_loc_slope[0] + offset[0],
        platform_loc_slope[1] + offset[1],
        platform_loc_slope[2] + offset[2] - platform_dim[2]/2
    )
    
    # Create cylinder (aligned along Z by default)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=wheel_pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"
    
    # Rotate 90° around Y to align with X-axis for rolling
    wheel.rotation_euler = (0.0, math.radians(90.0), 0.0)
    
    # Add rigid body (active - driven by physics)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheels.append(wheel)

# ===== CREATE HINGE CONSTRAINTS =====
for wheel in wheels:
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    pivot = bpy.context.active_object
    pivot.name = f"Hinge_Pivot_{wheel.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel.name}"
    
    # Configure constraint
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = platform
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_override_solver_iterations = True
    constraint.rigid_body_constraint.solver_iterations = 50
    
    # Set hinge axis to local X (global X after wheel rotation)
    constraint.rigid_body_constraint.hinge_axis = 'LOCAL_X'
    
    # Enable motor
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_type = 'VELOCITY'
    constraint.rigid_body_constraint.motor_velocity = motor_velocity
    
    # Link pivot to constraint
    constraint.parent = pivot

# ===== SCENE SETUP =====
# Set gravity (default is -9.8 Z)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.8)

# Set end frame for simulation
bpy.context.scene.frame_end = 300

# ===== VERIFICATION SETUP =====
# Add text output for debugging (optional, won't affect headless)
print(f"Climbing chassis created at slope base X={slope_start_x}")
print(f"Slope angle: {math.degrees(slope_angle):.1f}°")
print(f"Motor velocity: {motor_velocity} rad/s")
print(f"Expected forward speed: {motor_velocity * wheel_radius:.2f} m/s")