import bpy
import math
from mathutils import Vector, Euler

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 2.0, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
wheel_radius = 0.4
wheel_depth = 0.15
wheel_positions = [(1.5, 1.0), (-1.5, 1.0), (1.5, -1.0), (-1.5, -1.0)]
wheel_z = wheel_radius
steering_angle = 0.785398  # rad
steering_frames = 10
total_frames = 200
fps = 30
motion_distance = 10.0
diagonal_unit = Vector((0.70710678, 0.70710678, 0.0))
chassis_speed = motion_distance / (total_frames / fps)
chassis_velocity = diagonal_unit * chassis_speed

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.steps_per_second = fps
bpy.context.scene.frame_end = total_frames

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = Vector(chassis_dim)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'
chassis.rigid_body.collision_shape = 'BOX'

# Function to create a steerable wheel
def create_wheel(name, pos_xy):
    # Create cylinder (axis along Z by default)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=(pos_xy[0], pos_xy[1], wheel_z)
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate -90° about X so cylinder axis aligns with Y (rolling direction)
    wheel.rotation_euler = Euler((-math.pi/2, 0, 0), 'XYZ')
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CONVEX_HULL'
    wheel.rigid_body.angular_damping = 0.5
    
    # Create hinge constraint between wheel and chassis
    bpy.ops.rigidbody.constraint_add()
    hinge = bpy.context.active_object
    hinge.name = f"Hinge_{name}"
    hinge.rigid_body_constraint.type = 'HINGE'
    hinge.rigid_body_constraint.object1 = chassis
    hinge.rigid_body_constraint.object2 = wheel
    # Set pivot at wheel center
    hinge.location = wheel.location
    # Hinge axis is global Z for steering
    hinge.rigid_body_constraint.axis = 'Z'
    # Enable motor for steering
    hinge.rigid_body_constraint.use_motor = True
    hinge.rigid_body_constraint.motor_type = 'VELOCITY'
    hinge.rigid_body_constraint.motor_lin_target_velocity = 0.0
    hinge.rigid_body_constraint.motor_ang_target_velocity = steering_angle / (steering_frames / fps)
    
    # Keyframe motor angular velocity: active for steering_frames, then zero
    hinge.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity", frame=1)
    hinge.rigid_body_constraint.motor_ang_target_velocity = 0.0
    hinge.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity", frame=steering_frames+1)
    
    return wheel, hinge

# Create four wheels
wheels = []
hinges = []
wheel_names = ["Wheel_FR", "Wheel_FL", "Wheel_RR", "Wheel_RL"]
for name, pos in zip(wheel_names, wheel_positions):
    wheel, hinge = create_wheel(name, pos)
    wheels.append(wheel)
    hinges.append(hinge)

# Apply linear velocity to chassis for diagonal motion
chassis.rigid_body.linear_velocity = chassis_velocity
chassis.rigid_body.keyframe_insert(data_path="linear_velocity", frame=steering_frames+1)
chassis.rigid_body.linear_velocity = (0,0,0)
chassis.rigid_body.keyframe_insert(data_path="linear_velocity", frame=total_frames+1)

# Set initial frame
bpy.context.scene.frame_set(1)