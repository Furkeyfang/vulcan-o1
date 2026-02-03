import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
col_dim = (0.5, 0.5, 4.0)
col_loc = (0.0, 0.0, 2.0)
arm_dim = (6.0, 0.3, 0.3)
arm_loc = (3.0, 0.0, 4.0)
joint_pivot = (0.0, 0.0, 4.0)
hinge_axis = (0.0, 0.0, 1.0)
target_ang_vel = 0.05  # radians per frame
sim_frames = 300

# Create column (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.scale = col_dim
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create arm (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_dim
arm.name = "Arm"
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Create hinge constraint between column and arm
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Joint"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = column
constraint.rigid_body_constraint.object2 = arm
constraint.rigid_body_constraint.pivot_type = 'CUSTOM'
constraint.location = joint_pivot

# Set hinge axis (world Z)
constraint.rigid_body_constraint.use_limit_ang_z = False
constraint.rigid_body_constraint.use_motor_ang = True
constraint.rigid_body_constraint.motor_ang_target_velocity = target_ang_vel
constraint.rigid_body_constraint.motor_ang_max_impulse = 10.0  # Sufficient torque

# Set simulation end frame
bpy.context.scene.frame_end = sim_frames

# Optional: Set gravity to default (Z = -9.81)
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

print(f"Crane built. Arm angular velocity: {target_ang_vel} rad/frame")
print(f"Simulation will run for {sim_frames} frames.")