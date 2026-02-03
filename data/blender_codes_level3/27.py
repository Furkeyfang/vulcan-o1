import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
chassis_dim = (3.0, 1.0, 0.6)
chassis_loc = (0.0, 0.0, 0.7)
chassis_mass = 10.0
chassis_friction = 0.8

wheel_radius = 0.4
wheel_depth = 0.15
front_wheel_y = 1.5
rear_wheel_y = -1.5
wheel_center_z = 0.4
wheel_mass = 2.0
wheel_friction = 0.5

motor_velocity = 8.0
motor_torque = 5.0
hinge_axis = (1.0, 0.0, 0.0)

frame_end = 250

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 1.0

# Create chassis (streamlined body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[1]/2, chassis_dim[0]/2, chassis_dim[2]/2)  # half-extents
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.friction = chassis_friction
# Adjust center of mass downward (to bottom 1/3 of chassis)
chassis.rigid_body.use_margin = True
chassis.rigid_body.collision_margin = 0.01

# Create wheels (cylinders)
def create_wheel(name, y_pos):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=(0.0, y_pos, wheel_center_z),
        rotation=(0.0, math.radians(90.0), 0.0)  # Rotate so cylinder axis = X
    )
    wheel = bpy.context.active_object
    wheel.name = name
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.friction = wheel_friction
    return wheel

front_wheel = create_wheel("FrontWheel", front_wheel_y)
rear_wheel = create_wheel("RearWheel", rear_wheel_y)

# Create hinge constraints (motorized)
def create_motor_hinge(name, parent_obj, child_obj, pivot_loc):
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_loc)
    pivot = bpy.context.active_object
    pivot.name = name + "_Pivot"
    
    # Add constraint to parent (chassis)
    constraint = parent_obj.constraints.new('RIGID_BODY_JOINT')
    constraint.name = name
    constraint.object1 = parent_obj
    constraint.object2 = child_obj
    constraint.pivot_type = 'CUSTOM'
    constraint.pivot_x = pivot_loc[0]
    constraint.pivot_y = pivot_loc[1]
    constraint.pivot_z = pivot_loc[2]
    constraint.axis = hinge_axis
    constraint.use_motor = True
    constraint.motor_velocity = motor_velocity
    constraint.motor_max_impulse = motor_torque
    constraint.limit_lin_z = False  # Allow vertical movement
    constraint.limit_ang_y = True   # Prevent steering
    constraint.limit_ang_y_min = 0.0
    constraint.limit_ang_y_max = 0.0

# Hinge pivot locations at wheel centers
create_motor_hinge("FrontHinge", chassis, front_wheel, (0.0, front_wheel_y, wheel_center_z))
create_motor_hinge("RearHinge", chassis, rear_wheel, (0.0, rear_wheel_y, wheel_center_z))

# Set simulation parameters
bpy.context.scene.frame_end = frame_end
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Ensure proper collision shapes
chassis.rigid_body.collision_shape = 'BOX'
front_wheel.rigid_body.collision_shape = 'CYLINDER'
rear_wheel.rigid_body.collision_shape = 'CYLINDER'

# Set initial velocities to zero (start from rest)
chassis.rigid_body.kinematic = False
front_wheel.rigid_body.kinematic = False
rear_wheel.rigid_body.kinematic = False