import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
chassis_dim = (3.0, 1.5, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
wheel_radius = 0.4
wheel_depth = 0.15
wheel_positions = [
    (-1.1, 0.75, 0.4),
    (1.1, 0.75, 0.4),
    (-1.1, -0.75, 0.4),
    (1.1, -0.75, 0.4)
]
motor_velocity = 8.0
ground_size = 20.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 2.0  # Lightweight for acceleration

# Create wheels
wheels = []
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    wheel.rotation_euler = (0, math.radians(90), 0)  # Align rotation axis to X
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = 0.3  # Light wheels reduce rotational inertia
    wheels.append(wheel)

# Create hinge constraints with motors
for wheel in wheels:
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    pivot = bpy.context.active_object
    pivot.name = f"Pivot_{wheel.name}"
    pivot.rotation_euler = wheel.rotation_euler.copy()
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel.name}"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_limit_ang_z = True
    constraint.rigid_body_constraint.limit_ang_z_lower = 0
    constraint.rigid_body_constraint.limit_ang_z_upper = 0
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_ang_max_impulse = 5.0
    
    # Parent constraint to pivot
    constraint.parent = pivot

# Configure simulation
bpy.context.scene.frame_end = 200
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Set initial state (chassis at rest at origin)
chassis.location = (0, 0, chassis_loc[2])
for wheel in wheels:
    wheel.rigid_body.kinematic = False
    wheel.rigid_body.enabled = True

print("Motorized chassis assembly complete. Simulation ready.")
print(f"Target: Reach Y > {15.0}m within {200} frames.")