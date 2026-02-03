import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (6.0, 2.0, 0.5)
chassis_loc = (0.0, 0.0, 1.25)
wheel_radius = 0.5
wheel_depth = 0.2
wheel_corner_offsets = [(3.0, 1.0), (3.0, -1.0), (-3.0, 1.0), (-3.0, -1.0)]
wheel_z = 0.5  # chassis_loc[2] - chassis_dim[2]/2 - wheel_radius
ground_size = 100.0
motor_velocity = 4.5
chassis_mass = 10.0
wheel_mass = 1.0

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = (chassis_dim[0] / 2, chassis_dim[1] / 2, chassis_dim[2] / 2)  # Blender cube default size 2, so divide by 2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.collision_shape = 'BOX'

# Create wheels
wheels = []
for offset in wheel_corner_offsets:
    # Create cylinder (default aligned with Z, radius 1, depth 2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0, 
                                         location=(offset[0], offset[1], wheel_z))
    wheel = bpy.context.active_object
    # Rotate 90° around Y to align cylinder axis with X (for hinge axis)
    wheel.rotation_euler = (0, math.pi / 2, 0)
    # Scale: depth (X) = wheel_depth/2 (because default depth 2), radius (Y,Z) = wheel_radius/1
    wheel.scale = (wheel_depth / 2, wheel_radius, wheel_radius)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.collision_margin = 0.0  # Use shape margin
    wheel.rigid_body.rigid_body.collision_margin = 0.0  # Legacy property for some versions
    wheel.rigid_body.use_margin = True
    # Set cylinder axis to X (matches rotation)
    wheel.rigid_body.collision_shape = 'CYLINDER'
    # Note: In Blender 2.8+, the axis is automatically derived from object orientation.
    wheels.append(wheel)

# Create hinge constraints (motors) for each wheel
for wheel in wheels:
    # Create empty at wheel location for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.empty_display_size = 0.5
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = chassis
    constraint.object2 = wheel
    # Hinge axis is local X (vehicle longitudinal direction)
    constraint.axis = 'X'
    # Enable motor
    constraint.use_motor = True
    constraint.motor_angular_target_velocity = motor_velocity
    constraint.motor_max_impulse = 10.0  # Sufficient torque

# Set simulation parameters (optional, defaults are fine)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Output confirmation
print("Vehicle assembly complete. Chassis and 4 motorized wheels created.")