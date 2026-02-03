import bpy
import math

# ========== PARAMETERS ==========
chassis_dim = (5.0, 3.0, 0.5)
chassis_loc = (0.0, 0.0, 0.25)

wheel_radius = 0.6
wheel_depth = 0.25
wheel_offset_x = 2.5
wheel_offset_y = 1.5
wheel_center_z = 0.6

motor_velocity = 3.5

wheel_positions = [
    (wheel_offset_x, wheel_offset_y),
    (wheel_offset_x, -wheel_offset_y),
    (-wheel_offset_x, wheel_offset_y),
    (-wheel_offset_x, -wheel_offset_y)
]

# ========== SCENE SETUP ==========
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set rigid body world parameters for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 300

# ========== CREATE CHASSIS ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0], chassis_dim[1], chassis_dim[2])

# Add rigid body (active)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 20.0  # kg
chassis.rigid_body.friction = 0.5
chassis.rigid_body.restitution = 0.1
chassis.rigid_body.linear_damping = 0.04
chassis.rigid_body.angular_damping = 0.1
chassis.rigid_body.collision_shape = 'BOX'

# ========== CREATE WHEELS ==========
wheel_objects = []
for i, (wx, wy) in enumerate(wheel_positions):
    # Create cylinder (axis along Z initially)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=(wx, wy, wheel_center_z)
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    
    # Rotate 90° around Y so cylinder axis aligns with X (for X-axis rotation)
    wheel.rotation_euler = (0, math.radians(90), 0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 2.0
    wheel.rigid_body.friction = 1.0
    wheel.rigid_body.restitution = 0.05
    wheel.rigid_body.linear_damping = 0.1
    wheel.rigid_body.angular_damping = 0.2
    wheel.rigid_body.collision_shape = 'MESH'
    
    wheel_objects.append(wheel)

# ========== CREATE HINGE CONSTRAINTS ==========
for wheel in wheel_objects:
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    pivot = bpy.context.active_object
    pivot.name = f"Pivot_{wheel.name}"
    
    # Parent wheel to pivot (maintains transform)
    wheel.parent = pivot
    
    # Add rigid body constraint (hinge)
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel.name}"
    constraint.rigid_body_constraint.type = 'HINGE'
    
    # Set constraint objects
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = pivot
    
    # Position constraint at wheel center
    constraint.location = wheel.location
    
    # Align hinge axis with local X (after wheel rotation)
    # In constraint space: Z-axis is rotation axis, Y is disabled axis
    constraint.rigid_body_constraint.use_limit_ang_z = True
    constraint.rigid_body_constraint.limit_ang_z_lower = 0
    constraint.rigid_body_constraint.limit_ang_z_upper = 0
    
    # Enable motor
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_ang_max_impulse = 5.0

# ========== FINAL SETUP ==========
# Ensure all transforms are applied
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 0.8
ground.rigid_body.restitution = 0.1

print("Rover construction complete. Simulate 300 frames for forward travel.")