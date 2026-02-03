import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
chassis_dim = (1.5, 0.5, 0.3)
chassis_center_z = 0.15
wheel_radius = 0.4
wheel_depth = 0.15
chassis_half_x = 0.75
wheel_offset_x = chassis_half_x + wheel_depth/2.0
wheel_center_z = wheel_radius
left_wheel_pos = (-wheel_offset_x, 0.0, wheel_center_z)
right_wheel_pos = (wheel_offset_x, 0.0, wheel_center_z)
motor_target_velocity = 7.0
ground_z = 0.0
start_y = 0.0

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,ground_z))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 1.0
ground.rigid_body.restitution = 0.1

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, start_y, chassis_center_z))
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 5.0
chassis.rigid_body.friction = 0.5
chassis.rigid_body.collision_shape = 'BOX'
chassis.rigid_body.use_margin = True
chassis.rigid_body.collision_margin = 0.001

# Helper function to create wheel
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate cylinder so axis aligns with X (default cylinder axis is Z)
    wheel.rotation_euler = (0, math.pi/2.0, 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 1.0
    wheel.rigid_body.friction = 0.8
    wheel.rigid_body.collision_shape = 'CONVEX_HULL'
    wheel.rigid_body.use_margin = True
    wheel.rigid_body.collision_margin = 0.001
    wheel.rigid_body.linear_damping = 0.1
    wheel.rigid_body.angular_damping = 0.1
    return wheel

# Create wheels
left_wheel = create_wheel("Left_Wheel", left_wheel_pos)
right_wheel = create_wheel("Right_Wheel", right_wheel_pos)

# Helper function to create hinge constraint
def create_hinge(name, object1, object2, pivot_location, axis='X'):
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_location)
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = 0.2
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = object1
    constraint.object2 = object2
    constraint.use_limit_lin_z = True
    constraint.limit_lin_z_lower = 0.0
    constraint.limit_lin_z_upper = 0.0
    constraint.use_limit_ang_z = True
    constraint.limit_ang_z_lower = 0.0
    constraint.limit_ang_z_upper = 0.0
    # Set hinge axis
    if axis == 'X':
        constraint.use_limit_ang_x = True
        constraint.limit_ang_x_lower = -math.pi*2
        constraint.limit_ang_x_upper = math.pi*2
    # Enable motor
    constraint.use_motor_ang = True
    constraint.motor_ang_target_velocity = motor_target_velocity
    constraint.motor_ang_max_impulse = 0.0  # Auto-torque
    return constraint

# Create hinges at wheel centers
left_hinge = create_hinge("Left_Hinge", chassis, left_wheel, left_wheel_pos, 'X')
right_hinge = create_hinge("Right_Hinge", chassis, right_wheel, right_wheel_pos, 'X')

# Set simulation parameters
bpy.context.scene.frame_end = 125
bpy.context.scene.render.fps = 25
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Ensure all objects are awake
for obj in bpy.data.objects:
    if hasattr(obj, 'rigid_body') and obj.rigid_body is not None:
        obj.rigid_body.kinematic = False
        obj.rigid_body.use_deactivation = False

print("Vehicle construction complete. Ready for simulation.")