import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_rad = 1.0
base_h = 2.0
base_loc = (0.0, 0.0, 0.0)

arm_dim = (5.0, 0.5, 0.5)
arm_loc = (0.0, 0.0, 2.0)
arm_rot = (0.0, 0.0, 0.0)

pivot_base = (0.0, 0.0, 2.0)
pivot_arm = (0.0, 0.0, 0.0)
hinge_axis = (0.0, 0.0, 1.0)
motor_vel = 1.0
frame_end = 300

# Enable rigid body simulation
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Base Cylinder (Passive)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=base_rad,
    depth=base_h,
    location=base_loc
)
base = bpy.context.active_object
base.name = "Base"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
# Ensure it's fixed (passive rigid bodies are fixed by default in absence of constraints)

# Create Arm (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.rotation_euler = arm_rot
arm.scale = (arm_dim[0] / 2.0, arm_dim[1] / 2.0, arm_dim[2] / 2.0)  # Cube default size 2
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Create Hinge Constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_base)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Hinge_Constraint"
constraint_empty.empty_display_size = 0.5

bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = base
constraint.object2 = arm
constraint.pivot_type = 'LOCAL'
constraint.use_limit_angle = True
constraint.limit_angle_min = -math.pi
constraint.limit_angle_max = math.pi
# Motor settings
constraint.use_motor_angular = True
constraint.motor_angular_target_velocity = motor_vel
constraint.motor_angular_max_impulse = 10.0  # Sufficient torque

# Set constraint pivots in local coordinates
constraint.pivot_x = pivot_base[0]
constraint.pivot_y = pivot_base[1]
constraint.pivot_z = pivot_base[2]
# For object2 (arm), pivot is relative to arm's origin
constraint.pivot_x_2 = pivot_arm[0]
constraint.pivot_y_2 = pivot_arm[1]
constraint.pivot_z_2 = pivot_arm[2]
# Hinge axis (world Z)
constraint.axis_x = hinge_axis[0]
constraint.axis_y = hinge_axis[1]
constraint.axis_z = hinge_axis[2]

# Set simulation end frame
bpy.context.scene.frame_end = frame_end

# Optional: Set gravity to standard -Z if not already
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)