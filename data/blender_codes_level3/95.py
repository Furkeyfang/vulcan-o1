import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# ========== PARAMETERS ==========
# Vehicle dimensions
chassis_length = 3.0
chassis_width = 1.5
chassis_height = 0.4
chassis_center_z = 0.2

# Wheel properties
wheel_radius = 0.3
wheel_depth = 0.15
wheel_inset_factor = 0.7

# Calculated positions
front_y = chassis_width / 2
rear_y = -chassis_width / 2
front_x_offset = chassis_length/2 - wheel_radius * wheel_inset_factor
wheel_z = wheel_radius

front_left_pos = Vector((-front_x_offset, front_y, wheel_z))
front_right_pos = Vector((front_x_offset, front_y, wheel_z))
rear_left_pos = Vector((-front_x_offset, rear_y, wheel_z))
rear_right_pos = Vector((front_x_offset, rear_y, wheel_z))

# Axle properties
axle_radius = 0.05
axle_depth = 0.1
axle_z_offset = 0.05

# Physics parameters
chassis_mass = 50.0
wheel_mass = 5.0
steering_motor_velocity = 0.0
drive_motor_velocity = 2.0
steering_amplitude = 0.262  # 15 degrees in radians
steering_period = 150

# ========== CREATE CHASSIS ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, chassis_center_z))
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_length, chassis_width, chassis_height)

# Add rigid body
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.collision_shape = 'CONVEX_HULL'
chassis.rigid_body.friction = 0.8
chassis.rigid_body.restitution = 0.1

# ========== UTILITY FUNCTIONS ==========
def create_wheel(name, location, rotation, axis_orientation='Y'):
    """Create a wheel cylinder with proper orientation"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    
    # Orient cylinder axis
    if axis_orientation == 'X':
        wheel.rotation_euler = (0, math.pi/2, 0)
    elif axis_orientation == 'Y':
        wheel.rotation_euler = (math.pi/2, 0, 0)
    
    # Apply rotation
    wheel.rotation_euler = wheel.rotation_euler + rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.collision_margin = 0.01
    wheel.rigid_body.friction = 1.0
    
    return wheel

def create_axle(name, location, parent=None):
    """Create axle cylinder"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=axle_radius,
        depth=axle_depth,
        location=location
    )
    axle = bpy.context.active_object
    axle.name = name
    axle.rotation_euler = (0, math.pi/2, 0)  # Orient along X
    
    if parent:
        axle.parent = parent
    
    # Add rigid body (passive - fixed to parent)
    bpy.ops.rigidbody.object_add()
    axle.rigid_body.type = 'PASSIVE'
    
    return axle

def add_fixed_constraint(obj_a, obj_b, name):
    """Add fixed constraint between two objects"""
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = name
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    # Disable all motion
    constraint.rigid_body_constraint.use_limit_lin_x = True
    constraint.rigid_body_constraint.use_limit_lin_y = True
    constraint.rigid_body_constraint.use_limit_lin_z = True
    constraint.rigid_body_constraint.limit_lin_x_lower = 0
    constraint.rigid_body_constraint.limit_lin_x_upper = 0
    constraint.rigid_body_constraint.limit_lin_y_lower = 0
    constraint.rigid_body_constraint.limit_lin_y_upper = 0
    constraint.rigid_body_constraint.limit_lin_z_lower = 0
    constraint.rigid_body_constraint.limit_lin_z_upper = 0
    constraint.rigid_body_constraint.use_limit_ang_x = True
    constraint.rigid_body_constraint.use_limit_ang_y = True
    constraint.rigid_body_constraint.use_limit_ang_z = True
    constraint.rigid_body_constraint.limit_ang_x_lower = 0
    constraint.rigid_body_constraint.limit_ang_x_upper = 0
    constraint.rigid_body_constraint.limit_ang_y_lower = 0
    constraint.rigid_body_constraint.limit_ang_y_upper = 0
    constraint.rigid_body_constraint.limit_ang_z_lower = 0
    constraint.rigid_body_constraint.limit_ang_z_upper = 0

def add_hinge_constraint(obj_a, obj_b, name, axis, use_motor=False, motor_velocity=0.0):
    """Add hinge constraint with optional motor"""
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = name
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.rigid_body_constraint.use_limit_ang_z = True
    constraint.rigid_body_constraint.limit_ang_z_lower = -math.pi/3  # -60 degrees
    constraint.rigid_body_constraint.limit_ang_z_upper = math.pi/3   # +60 degrees
    
    # Set axis
    if axis == 'Z':
        constraint.rigid_body_constraint.use_angular_limit_z = True
    elif axis == 'X':
        # For X-axis hinge, we need to rotate the constraint object
        constraint.rotation_euler = (0, math.pi/2, 0)
    
    # Motor settings
    if use_motor:
        constraint.rigid_body_constraint.use_motor_ang = True
        constraint.rigid_body_constraint.motor_ang_velocity = motor_velocity
        constraint.rigid_body_constraint.motor_ang_max_torque = 100.0
    
    return constraint

# ========== CREATE FRONT WHEEL ASSEMBLIES ==========
# Front left
front_left_axle = create_axle(
    "FrontLeftAxle",
    front_left_pos + Vector((0, 0, axle_z_offset)),
    parent=chassis
)
front_left_wheel = create_wheel(
    "FrontLeftWheel",
    front_left_pos,
    rotation=(0, 0, 0),
    axis_orientation='X'
)

# Add constraints for front left
add_fixed_constraint(chassis, front_left_axle, "Fix_FrontLeftAxle")
front_left_hinge = add_hinge_constraint(
    front_left_axle,
    front_left_wheel,
    "Hinge_FrontLeft",
    axis='Z',
    use_motor=True,
    motor_velocity=steering_motor_velocity
)

# Front right
front_right_axle = create_axle(
    "FrontRightAxle",
    front_right_pos + Vector((0, 0, axle_z_offset)),
    parent=chassis
)
front_right_wheel = create_wheel(
    "FrontRightWheel",
    front_right_pos,
    rotation=(0, 0, 0),
    axis_orientation='X'
)

# Add constraints for front right
add_fixed_constraint(chassis, front_right_axle, "Fix_FrontRightAxle")
front_right_hinge = add_hinge_constraint(
    front_right_axle,
    front_right_wheel,
    "Hinge_FrontRight",
    axis='Z',
    use_motor=True,
    motor_velocity=steering_motor_velocity
)

# ========== CREATE REAR WHEEL ASSEMBLIES ==========
# Rear left
rear_left_axle = create_axle(
    "RearLeftAxle",
    rear_left_pos + Vector((0, 0, axle_z_offset)),
    parent=chassis
)
rear_left_wheel = create_wheel(
    "RearLeftWheel",
    rear_left_pos,
    rotation=(0, 0, 0),
    axis_orientation='X'
)

# Add constraints for rear left
add_fixed_constraint(chassis, rear_left_axle, "Fix_RearLeftAxle")
rear_left_hinge = add_hinge_constraint(
    rear_left_axle,
    rear_left_wheel,
    "Hinge_RearLeft",
    axis='X',
    use_motor=True,
    motor_velocity=drive_motor_velocity
)

# Rear right
rear_right_axle = create_axle(
    "RearRightAxle",
    rear_right_pos + Vector((0, 0, axle_z_offset)),
    parent=chassis
)
rear_right_wheel = create_wheel(
    "RearRightWheel",
    rear_right_pos,
    rotation=(0, 0, 0),
    axis_orientation='X'
)

# Add constraints for rear right
add_fixed_constraint(chassis, rear_right_axle, "Fix_RearRightAxle")
rear_right_hinge = add_hinge_constraint(
    rear_right_axle,
    rear_right_wheel,
    "Hinge_RearRight",
    axis='X',
    use_motor=True,
    motor_velocity=drive_motor_velocity
)

# ========== ANIMATE STEERING ==========
# Set up sinusoidal steering animation
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 60

# Animate front wheel steering motors
for frame in range(1, 301):
    steering_velocity = steering_amplitude * math.sin(2 * math.pi * frame / steering_period)
    
    scene.frame_set(frame)
    
    # Front left hinge
    front_left_hinge.rigid_body_constraint.motor_ang_velocity = steering_velocity
    front_left_hinge.keyframe_insert(data_path='rigid_body_constraint.motor_ang_velocity')
    
    # Front right hinge
    front_right_hinge.rigid_body_constraint.motor_ang_velocity = steering_velocity
    front_right_hinge.keyframe_insert(data_path='rigid_body_constraint.motor_ang_velocity')

# ========== FINAL SETUP ==========
# Add ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set up scene for physics simulation
scene.rigidbody_world.enabled = True
scene.rigidbody_world.substeps_per_frame = 10
scene.rigidbody_world.solver_iterations = 50

print("Vehicle construction complete. Run simulation with:")
print("blender --background vehicle.blend --python animate_vehicle.py")
print(f"Vehicle will follow sinusoidal path over {scene.frame_end} frames")