import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define variables from parameter summary
platform_dim = (3.0, 1.0, 0.3)
platform_loc = (0.0, 0.0, 0.3)

arm_dim = (1.5, 0.3, 0.3)
left_arm_rot_z = math.radians(-45.0)
right_arm_rot_z = math.radians(45.0)
left_arm_center = (-0.53033, 0.03033, 0.3)
right_arm_center = (0.53033, 1.03033, 0.3)

wheel_radius = 0.3
wheel_depth = 0.15
left_proximal_wheel_loc = (0.0, -0.5, 0.3)
left_distal_wheel_loc = (-1.06066, 0.56066, 0.3)
right_proximal_wheel_loc = (0.0, 0.5, 0.3)
right_distal_wheel_loc = (1.06066, 1.56066, 0.3)

left_motor_velocity = 6.0
right_motor_velocity = 4.0

ground_size = 20.0
total_frames = 300

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create central platform (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'BOX'

# Create left arm
bpy.ops.mesh.primitive_cube_add(size=1, location=left_arm_center)
left_arm = bpy.context.active_object
left_arm.name = "LeftArm"
left_arm.scale = arm_dim
left_arm.rotation_euler = (0, 0, left_arm_rot_z)
bpy.ops.rigidbody.object_add()
left_arm.rigid_body.type = 'ACTIVE'
left_arm.rigid_body.collision_shape = 'BOX'

# Create right arm
bpy.ops.mesh.primitive_cube_add(size=1, location=right_arm_center)
right_arm = bpy.context.active_object
right_arm.name = "RightArm"
right_arm.scale = arm_dim
right_arm.rotation_euler = (0, 0, right_arm_rot_z)
bpy.ops.rigidbody.object_add()
right_arm.rigid_body.type = 'ACTIVE'
right_arm.rigid_body.collision_shape = 'BOX'

# Function to create wheel with hinge constraint
def create_wheel(name, location, parent_arm, motor_velocity, axis='LOCAL_X'):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.rotation_euler = (0, math.radians(90), 0)  # Orient cylinder axis along X
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    
    # Create hinge constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"{name}_Hinge"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = parent_arm
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_angular_limit = True
    constraint.rigid_body_constraint.limit_ang_z_lower = 0
    constraint.rigid_body_constraint.limit_ang_z_upper = 0
    
    # Add motor
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    
    return constraint

# Create wheels with hinges
left_proximal_hinge = create_wheel(
    "LeftProximalWheel", 
    left_proximal_wheel_loc, 
    left_arm, 
    left_motor_velocity
)

left_distal_hinge = create_wheel(
    "LeftDistalWheel", 
    left_distal_wheel_loc, 
    left_arm, 
    left_motor_velocity
)

right_proximal_hinge = create_wheel(
    "RightProximalWheel", 
    right_proximal_wheel_loc, 
    right_arm, 
    right_motor_velocity
)

right_distal_hinge = create_wheel(
    "RightDistalWheel", 
    right_distal_wheel_loc, 
    right_arm, 
    right_motor_velocity
)

# Create fixed constraints between platform and arms
for arm, arm_name in [(left_arm, "LeftArm"), (right_arm, "RightArm")]:
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Platform_{arm_name}_Fixed"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = platform
    constraint.rigid_body_constraint.object2 = arm

# Set animation timeline
bpy.context.scene.frame_end = total_frames

# Activate all motors at frame 1 (already set in constraints)
# Set keyframes for motor activation
for hinge in [left_proximal_hinge, left_distal_hinge, right_proximal_hinge, right_distal_hinge]:
    hinge.rigid_body_constraint.keyframe_insert(data_path='motor_ang_target_velocity', frame=1)

# Enable rigid body simulation
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = bpy.data.collections['Collection']

print("Rover construction complete. Motors activated at frame 1.")