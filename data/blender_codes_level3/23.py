import bpy
import math
from mathutils import Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.2)
wheel_radius = 0.4
wheel_depth = 0.15
wheel_positions = [
    (1.5, 0.75, 0.0),
    (1.5, -0.75, 0.0),
    (-1.5, 0.75, 0.0),
    (-1.5, -0.75, 0.0)
]
ground_size = 50.0
ground_loc = (0.0, 0.0, -1.0)
motor_velocity = 5.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (rectangular prism)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Blender cube default size=2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.collision_shape = 'BOX'
chassis.rigid_body.mass = 2.0  # Heavier than wheels for stability

# Create wheels and constraints
wheel_names = ["Wheel_FR", "Wheel_FL", "Wheel_RR", "Wheel_RL"]
for i, (pos, name) in enumerate(zip(wheel_positions, wheel_names)):
    # Create cylinder (aligned with Z initially)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate cylinder 90° around Y to align with X-axis (hinge axis)
    wheel.rotation_euler = (0, math.pi/2, 0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.mass = 0.5
    
    # Create hinge constraint (empty object at wheel center)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{name}"
    constraint.empty_display_size = 0.5
    
    # Add rigid body constraint component
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    # Hinge axis: X (global)
    constraint.rotation_euler = (0, 0, 0)  # Ensure alignment
    constraint.rigid_body_constraint.use_limit_x = False
    # Enable motor
    constraint.rigid_body_constraint.use_motor_x = True
    constraint.rigid_body_constraint.motor_target_velocity_x = motor_velocity
    constraint.rigid_body_constraint.motor_max_impulse_x = 10.0  # Reasonable torque

# Set up world physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 250

# Optional: Add slight downward gravity tilt to ensure wheel contact
bpy.context.scene.gravity = (0, 0, -9.81)

print("Rover construction complete. Four motorized hinges active.")