import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.15)
arm_dim = (0.2, 0.2, 2.0)
arm_loc = (0.0, 0.0, 1.3)
proj_radius = 0.15
proj_depth = 0.3
proj_loc = (0.0, 0.0, 2.3)
hinge_axis = 'Y'
motor_torque = 1000.0
release_frame = 50
simulation_frames = 100
initial_hinge_angle = -1.5708  # -90° in radians

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = (base_dim[0]/2, base_dim[1]/2, base_dim[2]/2)  # Default cube is 2x2x2
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_dim[0]/2, arm_dim[1]/2, arm_dim[2]/2)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'

# Create Projectile (Cylinder aligned along X-axis)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=proj_radius,
    depth=proj_depth,
    location=proj_loc,
    rotation=(0.0, math.pi/2, 0.0)  # Rotate 90° around Y for X-axis alignment
)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = 1.0  # Default mass

# Create Fixed Constraint between Arm and Base
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.3))
fixed_empty = bpy.context.active_object
fixed_empty.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
fixed_empty.rigid_body_constraint.type = 'FIXED'
fixed_empty.rigid_body_constraint.object1 = base
fixed_empty.rigid_body_constraint.object2 = arm

# Create Hinge Constraint between Arm and Projectile
bpy.ops.object.empty_add(type='PLAIN_AXES', location=proj_loc)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge_empty.rigid_body_constraint.type = 'HINGE'
hinge_empty.rigid_body_constraint.object1 = arm
hinge_empty.rigid_body_constraint.object2 = projectile
hinge_empty.rigid_body_constraint.use_limit_ang_z = True
hinge_empty.rigid_body_constraint.limit_ang_z_lower = -3.1416  # -180°
hinge_empty.rigid_body_constraint.limit_ang_z_upper = 0.0       # 0°
hinge_empty.rigid_body_constraint.use_motor_ang = True
hinge_empty.rigid_body_constraint.motor_ang_target_velocity = 0.0
hinge_empty.rigid_body_constraint.motor_ang_max_torque = motor_torque

# Set initial hinge angle to -90° (pointing down)
hinge_empty.rotation_euler = (0.0, 0.0, initial_hinge_angle)

# Animate motor: enabled until release_frame, then disabled
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = simulation_frames

# Motor ON at frame 1
hinge_empty.rigid_body_constraint.use_motor_ang = True
hinge_empty.keyframe_insert(data_path='rigid_body_constraint.use_motor_ang', frame=1)

# Motor OFF at release_frame
hinge_empty.rigid_body_constraint.use_motor_ang = False
hinge_empty.keyframe_insert(data_path='rigid_body_constraint.use_motor_ang', frame=release_frame)

# Ensure smooth interpolation
for fcurve in hinge_empty.animation_data.action.fcurves:
    if 'use_motor_ang' in fcurve.data_path:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'CONSTANT'

# Set simulation substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Catapult assembly complete. Motor releases at frame", release_frame)