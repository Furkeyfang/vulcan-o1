import bpy
import math

# ===== 1. CLEAR SCENE =====
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ===== 2. DEFINE VARIABLES =====
# Chassis
chassis_loc = (0.0, 0.0, 0.4)
chassis_dim = (3.0, 1.5, 0.4)

# Wheels
wheel_radius = 0.3
wheel_depth = 0.15
wheel_clearance = 0.05
front_wheel_x = 1.45
rear_wheel_x = -1.45
wheel_y_offset = 0.675
wheel_z = 0.3

# Track Belts
belt_dim = (2.0, 0.1, 0.05)
belt_z = 0.025

# Steering
steering_angle_deg = 30.0
steering_angle_rad = math.radians(steering_angle_deg)
total_frames = 100

# ===== 3. CREATE CHASSIS =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0], chassis_dim[1], chassis_dim[2])
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'
chassis.rigid_body.collision_shape = 'BOX'

# ===== 4. CREATE WHEELS FUNCTION =====
def create_wheel(name, location, rotation):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location,
        rotation=rotation
    )
    wheel = bpy.context.active_object
    wheel.name = name
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.friction = 1.0
    wheel.rigid_body.use_margin = True
    wheel.rigid_body.collision_margin = 0.0
    return wheel

# ===== 5. CREATE ALL WHEELS =====
# Front Left (steerable)
front_left = create_wheel(
    "Front_Left_Wheel",
    (front_wheel_x, wheel_y_offset, wheel_z),
    (0.0, 0.0, 0.0)  # Cylinder default: axis along Z
)

# Front Right (steerable)
front_right = create_wheel(
    "Front_Right_Wheel",
    (front_wheel_x, -wheel_y_offset, wheel_z),
    (0.0, 0.0, 0.0)
)

# Rear Left (fixed)
rear_left = create_wheel(
    "Rear_Left_Wheel",
    (rear_wheel_x, wheel_y_offset, wheel_z),
    (0.0, 0.0, 0.0)
)

# Rear Right (fixed)
rear_right = create_wheel(
    "Rear_Right_Wheel",
    (rear_wheel_x, -wheel_y_offset, wheel_z),
    (0.0, 0.0, 0.0)
)

# ===== 6. CREATE TRACK BELTS =====
def create_track_belt(name, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    belt = bpy.context.active_object
    belt.name = name
    belt.scale = (belt_dim[0], belt_dim[1], belt_dim[2])
    bpy.ops.rigidbody.object_add()
    belt.rigid_body.type = 'ACTIVE'
    belt.rigid_body.collision_shape = 'BOX'
    belt.rigid_body.friction = 2.0  # Higher friction for track-like behavior
    return belt

# Left Track Belt
left_belt = create_track_belt(
    "Left_Track_Belt",
    (0.0, wheel_y_offset, belt_z)
)

# Right Track Belt
right_belt = create_track_belt(
    "Right_Track_Belt",
    (0.0, -wheel_y_offset, belt_z)
)

# ===== 7. ADD CONSTRAINTS =====
# Function to add constraint between two objects
def add_constraint(obj1, obj2, const_type, location, use_limit=False, limit_min=0, limit_max=0):
    # Create empty object for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = const_type
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    # Set limits for hinge
    if use_limit and const_type == 'HINGE':
        constraint.use_limit_ang_z = True
        constraint.limit_ang_z_lower = limit_min
        constraint.limit_ang_z_upper = limit_max
    
    return constraint

# Fixed constraints for rear wheels
add_constraint(chassis, rear_left, 'FIXED', rear_left.location)
add_constraint(chassis, rear_right, 'FIXED', rear_right.location)

# Hinge constraints for front wheels (steering)
front_left_hinge = add_constraint(
    chassis, front_left, 'HINGE',
    front_left.location,
    use_limit=True,
    limit_min=-steering_angle_rad,
    limit_max=steering_angle_rad
)

front_right_hinge = add_constraint(
    chassis, front_right, 'HINGE',
    front_right.location,
    use_limit=True,
    limit_min=-steering_angle_rad,
    limit_max=steering_angle_rad
)

# ===== 8. SET UP STEERING MOTORS =====
# Configure hinge constraints as motors
def configure_steering_motor(constraint, target_angle):
    constraint.use_motor_ang_z = True
    constraint.motor_ang_z_type = 'POSITION'  # Angular position control
    constraint.motor_ang_z_target_position = target_angle
    constraint.motor_ang_z_stiffness = 100.0  # High stiffness for precise control
    constraint.motor_ang_z_damping = 10.0     # Reasonable damping

# Steer left: both wheels turn 30 degrees left
configure_steering_motor(front_left_hinge, steering_angle_rad)   # Left turn
configure_steering_motor(front_right_hinge, steering_angle_rad)  # Left turn

# ===== 9. SCENE SETUP FOR PHYSICS =====
# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Set frame range for simulation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = total_frames

# Set physics substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# ===== 10. ACTIVATE PHYSICS ANIMATION =====
# Enable physics for all frames
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = total_frames

print(f"Crawler vehicle created with steering mechanism.")
print(f"Front wheels set to {steering_angle_deg}° left turn.")
print(f"Physics simulation ready for {total_frames} frames.")