import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.2)
wheel_radius = 0.3
wheel_depth = 0.15
front_x = 1.425
rear_x = -1.425
left_y = -0.75
right_y = 0.75
wheel_z = 0.3
target_velocity = 15.0

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 20.0  # Reasonable mass for vehicle

# Wheel creation function
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location,
        rotation=(0, math.pi/2, 0)  # Rotate for X-axis alignment
    )
    wheel = bpy.context.active_object
    wheel.name = name
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = 2.0
    return wheel

# Create wheels
fl_wheel = create_wheel("FrontLeftWheel", (front_x, left_y, wheel_z))
fr_wheel = create_wheel("FrontRightWheel", (front_x, right_y, wheel_z))
rl_wheel = create_wheel("RearLeftWheel", (rear_x, left_y, wheel_z))
rr_wheel = create_wheel("RearRightWheel", (rear_x, right_y, wheel_z))

# Constraint creation function
def create_constraint(name, obj1, obj2, location, constraint_type, use_motor=False):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = constraint_type
    constraint.object1 = obj1
    constraint.object2 = obj2
    if constraint_type == 'HINGE':
        constraint.use_limit_x = True
        constraint.limit_x_lower = 0
        constraint.limit_x_upper = 0
        if use_motor:
            constraint.use_motor_x = True
            constraint.motor_target_velocity_x = target_velocity
            constraint.motor_max_impulse_x = 10.0
    return constraint

# Create constraints
create_constraint("FrontLeftHinge", chassis, fl_wheel, fl_wheel.location, 'HINGE', use_motor=True)
create_constraint("FrontRightHinge", chassis, fr_wheel, fr_wheel.location, 'HINGE', use_motor=True)
create_constraint("RearLeftFixed", chassis, rl_wheel, rl_wheel.location, 'FIXED')
create_constraint("RearRightFixed", chassis, rr_wheel, rr_wheel.location, 'FIXED')

# Setup world physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 200

# Add ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,-0.01))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'