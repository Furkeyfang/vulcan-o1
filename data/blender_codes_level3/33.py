import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
chassis_dim = (6.0, 3.0, 1.0)
chassis_loc = (0.0, 0.0, 0.8)
chassis_mass = 1000.0
wheel_radius = 0.8
wheel_depth = 0.3
wheel_mass = 50.0
wheel_locations = [
    (3.0, 1.5, 0.8),
    (3.0, -1.5, 0.8),
    (-3.0, 1.5, 0.8),
    (-3.0, -1.5, 0.8)
]
hinge_axis = (0.0, 1.0, 0.0)  # Y-axis for forward drive (X-direction motion)
motor_velocity = 3.0
ground_size = (40.0, 40.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)
simulation_frames = 300

# Create Ground Plane
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 1.0
ground.rigid_body.restitution = 0.1

# Create Chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.friction = 0.5
chassis.rigid_body.restitution = 0.1

# Create Wheels
wheels = []
for i, loc in enumerate(wheel_locations):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=loc
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    # Rotate cylinder 90° around X so its axis aligns with Y (for hinge around Y)
    wheel.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.friction = 1.0
    wheel.rigid_body.restitution = 0.1
    wheels.append(wheel)

# Create Hinge Constraints (Motors)
for wheel in wheels:
    # Create hinge constraint empty at wheel location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    constraint_obj = bpy.context.active_object
    constraint_obj.name = f"Hinge_{wheel.name}"
    constraint_obj.empty_display_size = 1.0
    
    # Add rigid body constraint component
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_obj.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = chassis
    constraint.object2 = wheel
    constraint.use_angular_friction = True
    constraint.angular_friction = 0.1  # Small damping
    
    # Enable motor
    constraint.use_motor_angular = True
    constraint.motor_angular_target_velocity = motor_velocity
    constraint.motor_angular_max_impulse = 1000.0  # High torque for heavy chassis
    
    # Set hinge axis (Y-axis for forward drive)
    constraint.axis = hinge_axis

# Set up scene physics
scene = bpy.context.scene
scene.frame_end = simulation_frames
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

# Optional: Set initial linear damping to reduce wobble
chassis.rigid_body.linear_damping = 0.1
for wheel in wheels:
    wheel.rigid_body.angular_damping = 0.05

print("Heavy chassis assembly complete. All four wheels are motorized.")