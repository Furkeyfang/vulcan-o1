import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
chassis_length = 6.0
chassis_width = 3.0
chassis_height = 1.0
chassis_center = (0.0, 0.0, 0.5)
wheel_radius = 0.6
wheel_depth = 0.3
wheel_positions = [(2.85, 1.5, 0.6), (2.85, -1.5, 0.6), (-2.85, 1.5, 0.6), (-2.85, -1.5, 0.6)]
motor_velocity = 3.5
block_size = 1.0
block_left_center = (4.5, -0.75, 0.5)
block_right_center = (4.5, 0.75, 0.5)
ground_size = 30.0
simulation_frames = 300

# Enable rigidbody physics
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = bpy.data.collections.new("RigidBodyWorld")
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 1.0
ground.rigid_body.restitution = 0.1

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_center)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_length, chassis_width, chassis_height)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 50.0
chassis.rigid_body.friction = 0.8
chassis.rigid_body.restitution = 0.1

# Create wheels
wheel_names = []
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    wheel.rotation_euler = (0, math.pi/2, 0)  # Rotate for X-axis alignment
    
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 5.0
    wheel.rigid_body.friction = 1.2  # High friction for traction
    wheel.rigid_body.restitution = 0.1
    
    wheel_names.append(wheel.name)

# Create hinge constraints for wheels
for wheel_name in wheel_names:
    wheel = bpy.data.objects[wheel_name]
    
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    pivot = bpy.context.active_object
    pivot.name = f"Pivot_{wheel_name}"
    
    # Parent wheel to pivot (maintains transform)
    wheel.parent = pivot
    
    # Create constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel_name}"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = pivot
    
    # Set hinge axis to local X
    constraint.rigid_body_constraint.use_breaking = False
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_lin_target_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_lin_target_velocity = 0  # Linear motor not used
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    
    # Position constraint at wheel location
    constraint.location = wheel.location

# Create passive blocks
bpy.ops.mesh.primitive_cube_add(size=1.0, location=block_left_center)
block_left = bpy.context.active_object
block_left.name = "Block_Left"
block_left.scale = (block_size, block_size, block_size)
bpy.ops.rigidbody.object_add()
block_left.rigid_body.type = 'PASSIVE'
block_left.rigid_body.mass = 10.0
block_left.rigid_body.friction = 0.6
block_left.rigid_body.restitution = 0.2

bpy.ops.mesh.primitive_cube_add(size=1.0, location=block_right_center)
block_right = bpy.context.active_object
block_right.name = "Block_Right"
block_right.scale = (block_size, block_size, block_size)
bpy.ops.rigidbody.object_add()
block_right.rigid_body.type = 'PASSIVE'
block_right.rigid_body.mass = 10.0
block_right.rigid_body.friction = 0.6
block_right.rigid_body.restitution = 0.2

# Set collision margins for stability
for obj in bpy.data.objects:
    if hasattr(obj, 'rigid_body'):
        obj.rigid_body.collision_margin = 0.04

# Ensure proper layer assignment for rigidbody world
rbw = bpy.context.scene.rigidbody_world
for obj in [chassis, ground, block_left, block_right] + [bpy.data.objects[wn] for wn in wheel_names]:
    if obj.name not in rbw.collection.objects:
        rbw.collection.objects.link(obj)

print("Motorized chassis assembly complete. Simulation ready for 300 frames.")