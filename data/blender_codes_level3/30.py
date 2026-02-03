import bpy
import mathutils

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define variables from parameter summary
chassis_dim = (3.0, 1.0, 0.5)
chassis_loc = (0.0, 0.0, 0.25)

wheel_radius = 0.3
wheel_depth = 0.15

wheel_positions = {
    "front_left": (-1.0, 0.5, 0.0),
    "front_right": (-1.0, -0.5, 0.0),
    "rear_left": (1.0, 0.5, 0.0),
    "rear_right": (1.0, -0.5, 0.0)
}

hinge_axis = (1.0, 0.0, 0.0)
motor_start_velocity = 0.0
motor_target_velocity = 9.0
acceleration_start_frame = 1
acceleration_end_frame = 50
verification_frame = 200
verification_threshold_y = 20.0

# 3. Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 4. Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# 5. Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Blender cube radius=1
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 5.0
chassis.rigid_body.friction = 0.8
chassis.rigid_body.linear_damping = 0.1
chassis.rigid_body.angular_damping = 0.1

# 6. Create wheels and hinge constraints
wheels = []
for wheel_name, wheel_pos in wheel_positions.items():
    # Create cylinder (aligned along Y initially)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=wheel_pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{wheel_name}"
    
    # Rotate cylinder to align with X-axis (depth becomes width)
    wheel.rotation_euler = (0, 0, math.pi/2)
    
    # Apply rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = 0.5
    wheel.rigid_body.friction = 1.2
    wheels.append(wheel)
    
    # Create hinge constraint between chassis and wheel
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel_pos)
    hinge_empty = bpy.context.active_object
    hinge_empty.name = f"Hinge_{wheel_name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = hinge_empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = chassis
    constraint.object2 = wheel
    constraint.pivot_type = 'CENTER'
    constraint.use_linear_limit = True
    constraint.limit_lin_x_lower = 0
    constraint.limit_lin_x_upper = 0
    constraint.limit_lin_y_lower = 0
    constraint.limit_lin_y_upper = 0
    constraint.limit_lin_z_lower = 0
    constraint.limit_lin_z_upper = 0
    constraint.use_angular_limit = True
    constraint.limit_ang_z_lower = 0
    constraint.limit_ang_z_upper = 0
    constraint.limit_ang_y_lower = 0
    constraint.limit_ang_y_upper = 0
    constraint.axis = hinge_axis
    
    # Enable motor with animated velocity
    constraint.use_motor_angular = True
    constraint.motor_angular_target_velocity = motor_start_velocity
    
    # Keyframe acceleration sequence
    constraint.keyframe_insert(data_path="motor_angular_target_velocity", frame=acceleration_start_frame)
    constraint.motor_angular_target_velocity = motor_target_velocity
    constraint.keyframe_insert(data_path="motor_angular_target_velocity", frame=acceleration_end_frame)

# 7. Set simulation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = verification_frame

# 8. Verification setup (would be checked after simulation bake)
print("Robot construction complete. Bake simulation to verify Y-displacement > 20m.")