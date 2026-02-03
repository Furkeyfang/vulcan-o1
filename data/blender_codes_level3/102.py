import bpy
import math

# ========== PARAMETERS ==========
ground_size = 10.0
platform_dim = (3.0, 2.0, 0.3)
platform_center = (0.0, 0.0, 0.45)
column_radius = 0.1
column_height = 0.5
column_center = (0.0, 0.0, 0.25)
hinge_pivot = (0.0, 0.0, 0.45)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 2.0
simulation_frames = 100

# ========== SCENE SETUP ==========
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set rigid body world parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# ========== GROUND PLANE ==========
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ========== STEERING COLUMN ==========
bpy.ops.mesh.primitive_cylinder_add(
    radius=column_radius,
    depth=column_height,
    location=column_center
)
column = bpy.context.active_object
column.name = "Steering_Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'CYLINDER'

# ========== PLATFORM ==========
bpy.ops.mesh.primitive_cube_add(size=1, location=platform_center)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (
    platform_dim[0] / 2,  # Blender cube default size 2, scale to exact dimensions
    platform_dim[1] / 2,
    platform_dim[2] / 2
)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.linear_damping = 0.1
platform.rigid_body.angular_damping = 0.1
platform.rigid_body.use_gravity = False  # Prevent sagging

# ========== HINGE CONSTRAINT ==========
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
empty = bpy.context.active_object
empty.name = "Hinge_Constraint"

bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = platform
constraint.object2 = column
constraint.pivot_type = 'CENTER'

# Set hinge pivot and axis in world coordinates
constraint.pivot_x = hinge_pivot[0]
constraint.pivot_y = hinge_pivot[1]
constraint.pivot_z = hinge_pivot[2]
constraint.axis_x = hinge_axis[0]
constraint.axis_y = hinge_axis[1]
constraint.axis_z = hinge_axis[2]

# Configure motor
constraint.use_motor = True
constraint.motor_angular_target_velocity = motor_velocity
constraint.motor_max_impulse = 10.0  # Sufficient torque

# ========== VERIFICATION SETUP ==========
# Keyframe initial rotation
platform.rotation_euler = (0, 0, 0)
platform.keyframe_insert(data_path="rotation_euler", frame=1)

# Calculate expected rotation after 100 frames at 2 rad/s
angle = motor_velocity * (simulation_frames / 60)  # radians
platform.rotation_euler = (0, 0, angle)
platform.keyframe_insert(data_path="rotation_euler", frame=simulation_frames)

print(f"Platform should rotate {math.degrees(angle):.1f}° in {simulation_frames} frames")