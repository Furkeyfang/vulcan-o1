import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
chassis_size = (6.0, 3.0, 0.8)
chassis_loc = (0.0, 0.0, 0.4)
wheel_rad = 0.6
wheel_depth = 0.3
row_y = [-1.5, 1.5]
wheel_x = [2.4, 0.0, -2.4]
wheel_z = 0.6
motor_vel = 4.5
sim_frames = 300
anchor_sz = 0.1

# Create Ground Anchor (small passive object at origin)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
anchor = bpy.context.active_object
anchor.name = "Ground_Anchor"
anchor.scale = (anchor_sz, anchor_sz, anchor_sz)
bpy.ops.rigidbody.object_add()
anchor.rigid_body.type = 'PASSIVE'

# Create Chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_size[0]/2, chassis_size[1]/2, chassis_size[2]/2)  # Blender cube size=2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 100.0  # Heavy chassis

# Create Fixed Constraint between Chassis and Anchor
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Constraint"
fixed_constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint = fixed_constraint.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = chassis
constraint.object2 = anchor
constraint.disable_collisions = True

# Create Wheels and Hinge Constraints
wheel_objects = []
for y_pos in row_y:
    for x_pos in wheel_x:
        # Create wheel (cylinder along Y-axis)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=wheel_rad,
            depth=wheel_depth,
            location=(x_pos, y_pos, wheel_z),
            rotation=(0, 0, math.pi/2)  # Rotate 90° so cylinder axis is Y
        )
        wheel = bpy.context.active_object
        wheel.name = f"Wheel_X{x_pos:.1f}_Y{y_pos:.1f}"
        bpy.ops.rigidbody.object_add()
        wheel.rigid_body.type = 'ACTIVE'
        wheel.rigid_body.mass = 10.0  # Reasonable wheel mass
        wheel.rigid_body.friction = 1.0
        wheel.rigid_body.use_margin = True
        wheel.rigid_body.collision_margin = 0.0
        
        # Create hinge constraint at wheel center
        bpy.ops.object.empty_add(
            type='SINGLE_ARROW',
            location=(x_pos, y_pos, wheel_z),
            rotation=(0, math.pi/2, 0)  # Arrow points along X-axis
        )
        hinge = bpy.context.active_object
        hinge.name = f"Hinge_X{x_pos:.1f}_Y{y_pos:.1f}"
        hinge.empty_display_size = 0.8
        bpy.ops.rigidbody.constraint_add()
        h_constraint = hinge.rigid_body_constraint
        h_constraint.type = 'HINGE'
        h_constraint.object1 = wheel
        h_constraint.object2 = chassis
        h_constraint.use_limit_ang_z = False
        h_constraint.use_motor_ang = True
        h_constraint.motor_ang_target_velocity = motor_vel
        h_constraint.motor_ang_max_impulse = 100.0
        
        wheel_objects.append(wheel)

# Set simulation parameters
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Keyframe motor activation (start at frame 1)
bpy.context.scene.frame_set(1)
for wheel in wheel_objects:
    # Find associated hinge constraint
    for obj in bpy.data.objects:
        if obj.rigid_body_constraint and obj.rigid_body_constraint.object1 == wheel:
            obj.rigid_body_constraint.motor_ang_target_velocity = motor_vel
            obj.keyframe_insert(data_path='rigid_body_constraint.motor_ang_target_velocity')

# Keyframe fixed constraint release (disable at frame 1)
bpy.context.scene.frame_set(0)
fixed_constraint.rigid_body_constraint.enabled = True
fixed_constraint.keyframe_insert(data_path='rigid_body_constraint.enabled')
bpy.context.scene.frame_set(1)
fixed_constraint.rigid_body_constraint.enabled = False
fixed_constraint.keyframe_insert(data_path='rigid_body_constraint.enabled')

# Reset to frame 0 for simulation start
bpy.context.scene.frame_set(0)

print("Chassis assembly complete. Simulation ready.")
print(f"Target: Move +20m in {sim_frames} frames with motor velocity {motor_vel}")