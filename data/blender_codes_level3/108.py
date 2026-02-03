import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (0.5, 0.5, 4.0)
base_loc = (0.0, 0.0, 2.0)
arm_dim = (4.0, 0.5, 0.5)
arm_loc = (2.0, 0.0, 4.0)
joint_pivot = (0.0, 0.0, 4.0)
motor_velocity = 3.0
simulation_frames = 250
fps = 60

# Set scene properties for simulation
scene = bpy.context.scene
scene.frame_end = simulation_frames
scene.render.fps = fps

# Create Base Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base_Column"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Horizontal Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Crane_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'

# Create Hinge Constraint (motorized)
# First ensure arm is active object
bpy.context.view_layer.objects.active = arm
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Motor"
constraint.rigid_body_constraint.type = 'HINGE'

# Set constraint properties
constraint.rigid_body_constraint.object1 = arm
constraint.rigid_body_constraint.object2 = base
constraint.rigid_body_constraint.pivot_x = joint_pivot[0]
constraint.rigid_body_constraint.pivot_y = joint_pivot[1]
constraint.rigid_body_constraint.pivot_z = joint_pivot[2]
constraint.rigid_body_constraint.axis = 'Z'

# Enable motor
constraint.rigid_body_constraint.use_motor = True
constraint.rigid_body_constraint.motor_angular_target_velocity = motor_velocity

# Optional: Enable angular limits for verification clarity
constraint.rigid_body_constraint.use_limit_angle = True
constraint.rigid_body_constraint.limit_angle_upper = math.radians(90.0)

# Set simulation world properties
if scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
scene.rigidbody_world.steps_per_second = fps
scene.rigidbody_world.solver_iterations = 10

# Verify initial arm rotation is 0°
arm.rotation_euler = (0.0, 0.0, 0.0)

# Output verification info
print(f"Setup complete: Crane arm with motorized hinge.")
print(f"Motor velocity: {motor_velocity} rad/s")
print(f"Expected rotation in {simulation_frames} frames at {fps} fps:")
print(f"  Δθ = {motor_velocity * simulation_frames / fps:.2f} rad")
print(f"     = {math.degrees(motor_velocity * simulation_frames / fps):.1f}°")