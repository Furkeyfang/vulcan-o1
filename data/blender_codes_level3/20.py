import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
chassis_dim = (2.0, 1.0, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
wheel_radius = 0.25
wheel_depth = 0.1
front_wheel_loc = (1.0, 0.0, 0.25)
rear_wheel_loc = (-1.0, 0.0, 0.25)
hinge_axis = (1.0, 0.0, 0.0)
motor_velocity = 5.5
ground_size = 20.0
ground_loc = (0.0, 0.0, -0.01)
wheel_friction = 1.2
ground_friction = 0.8
simulation_frames = 250
target_distance = 9.0

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = simulation_frames

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = ground_friction
ground.rigid_body.restitution = 0.1

# Create chassis (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Scale from center
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 5.0
chassis.rigid_body.friction = 0.5
chassis.rigid_body.linear_damping = 0.0
chassis.rigid_body.angular_damping = 0.1

# Function to create wheel
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° around Y to align cylinder axis with X
    wheel.rotation_euler = (0.0, math.radians(90.0), 0.0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 1.0
    wheel.rigid_body.friction = wheel_friction
    wheel.rigid_body.linear_damping = 0.0
    wheel.rigid_body.angular_damping = 0.0
    return wheel

# Create wheels
front_wheel = create_wheel("Front_Wheel", front_wheel_loc)
rear_wheel = create_wheel("Rear_Wheel", rear_wheel_loc)

# Create hinge constraints between chassis and wheels
def create_motor_hinge(wheel, chassis, axis):
    # Add constraint to wheel
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel.name}"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = wheel
    constraint.rigid_body_constraint.object2 = chassis
    constraint.rigid_body_constraint.use_limit_lin_x = True
    constraint.rigid_body_constraint.use_limit_lin_y = True
    constraint.rigid_body_constraint.use_limit_lin_z = True
    constraint.rigid_body_constraint.use_limit_ang_x = False
    constraint.rigid_body_constraint.use_limit_ang_y = True
    constraint.rigid_body_constraint.use_limit_ang_z = True
    # Set hinge axis in local space of wheel (already rotated)
    constraint.rigid_body_constraint.axis_ang_x = axis[0]
    constraint.rigid_body_constraint.axis_ang_y = axis[1]
    constraint.rigid_body_constraint.axis_ang_z = axis[2]
    # Configure motor
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_ang_max_impulse = 10.0
    # Position constraint at wheel center
    constraint.location = wheel.location

create_motor_hinge(front_wheel, chassis, hinge_axis)
create_motor_hinge(rear_wheel, chassis, hinge_axis)

# Ensure motors are active from frame 1
for obj in bpy.data.objects:
    if obj.rigid_body_constraint and obj.rigid_body_constraint.use_motor_ang:
        obj.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
        # Keyframe motor activation at frame 1
        obj.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity", frame=1)

# Set initial state: all objects at rest
for obj in [chassis, front_wheel, rear_wheel]:
    obj.rigid_body.kinematic = False
    obj.keyframe_insert(data_path="rigid_body.kinematic", frame=1)

print(f"Rover constructed. Simulation will run for {simulation_frames} frames.")
print(f"Target: Y-coordinate > {target_distance} meters.")