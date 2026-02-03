import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
mast_r = 0.2
mast_h = 5.0
mast_loc = (0.0, 0.0, 2.5)
arm_dim = (4.0, 0.4, 0.4)
arm_loc = (2.0, 0.0, 4.0)
counter_dim = (0.8, 0.8, 0.8)
counter_loc = (-0.8, 0.0, 2.0)
hook_dim = (0.2, 0.2, 0.2)
hook_loc = (4.0, 0.0, 4.0)
load_dim = (0.5, 0.5, 0.5)
load_mass = 600.0
load_init_loc = (4.0, 0.0, 0.25)
arm_hinge_z = 4.0
counter_hinge_z = 2.0
arm_motor_v = 0.5
hook_motor_v = 0.2

# Create Mast (fixed to ground)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=mast_r,
    depth=mast_h,
    location=mast_loc
)
mast = bpy.context.active_object
mast.name = "Mast"
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'PASSIVE'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_dim[0]/2, arm_dim[1]/2, arm_dim[2]/2)  # Cube primitive size=2
bpy.ops.rigidbody.object_add()
arm.rigid_body.mass = arm_dim[0] * arm_dim[1] * arm_dim[2] * 2500  # Steel density

# Create Counterweight
bpy.ops.mesh.primitive_cube_add(size=1, location=counter_loc)
counter = bpy.context.active_object
counter.name = "Counterweight"
counter.scale = (counter_dim[0]/2, counter_dim[1]/2, counter_dim[2]/2)
bpy.ops.rigidbody.object_add()
counter.rigid_body.mass = counter_dim[0] * counter_dim[1] * counter_dim[2] * 2500

# Create Hook
bpy.ops.mesh.primitive_cube_add(size=1, location=hook_loc)
hook = bpy.context.active_object
hook.name = "Hook"
hook.scale = (hook_dim[0]/2, hook_dim[1]/2, hook_dim[2]/2)
bpy.ops.rigidbody.object_add()
hook.rigid_body.mass = hook_dim[0] * hook_dim[1] * hook_dim[2] * 2500

# Create Load
bpy.ops.mesh.primitive_cube_add(size=1, location=load_init_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass

# Constraints
# 1. Arm hinge to mast
bpy.ops.rigidbody.constraint_add()
arm_constraint = bpy.context.active_object
arm_constraint.name = "Arm_Hinge"
arm_constraint.rigid_body_constraint.type = 'HINGE'
arm_constraint.rigid_body_constraint.object1 = mast
arm_constraint.rigid_body_constraint.object2 = arm
arm_constraint.location = (0, 0, arm_hinge_z)
arm_constraint.rigid_body_constraint.use_limit_ang_z = True
arm_constraint.rigid_body_constraint.limit_ang_z_lower = -math.pi/2
arm_constraint.rigid_body_constraint.limit_ang_z_upper = math.pi/2
arm_constraint.rigid_body_constraint.use_motor_ang_z = True
arm_constraint.rigid_body_constraint.motor_ang_z_velocity = arm_motor_v

# 2. Counterweight fixed to mast
bpy.ops.rigidbody.constraint_add()
counter_constraint = bpy.context.active_object
counter_constraint.name = "Counter_Fixed"
counter_constraint.rigid_body_constraint.type = 'FIXED'
counter_constraint.rigid_body_constraint.object1 = mast
counter_constraint.rigid_body_constraint.object2 = counter
counter_constraint.location = (0, 0, counter_hinge_z)

# 3. Hook hinge to arm
bpy.ops.rigidbody.constraint_add()
hook_constraint = bpy.context.active_object
hook_constraint.name = "Hook_Hinge"
hook_constraint.rigid_body_constraint.type = 'HINGE'
hook_constraint.rigid_body_constraint.object1 = arm
hook_constraint.rigid_body_constraint.object2 = hook
hook_constraint.location = hook_loc
hook_constraint.rigid_body_constraint.axis_ang_y = 1.0  # Y-axis rotation
hook_constraint.rigid_body_constraint.use_limit_ang_y = True
hook_constraint.rigid_body_constraint.limit_ang_y_lower = -math.pi/2
hook_constraint.rigid_body_constraint.limit_ang_y_upper = 0
hook_constraint.rigid_body_constraint.use_motor_ang_y = True
hook_constraint.rigid_body_constraint.motor_ang_y_velocity = hook_motor_v

# 4. Load fixed to hook (initially disabled - will enable during simulation)
bpy.ops.rigidbody.constraint_add()
load_constraint = bpy.context.active_object
load_constraint.name = "Load_Fixed"
load_constraint.rigid_body_constraint.type = 'FIXED'
load_constraint.rigid_body_constraint.object1 = hook
load_constraint.rigid_body_constraint.object2 = load
load_constraint.rigid_body_constraint.enabled = False  # Disabled initially

# Setup animation timeline
bpy.context.scene.frame_end = 500
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Motor control keyframes
# Hook motor: active frames 0-200 (lower and lift)
hook_constraint.rigid_body_constraint.motor_ang_y_velocity = hook_motor_v
hook_constraint.keyframe_insert(data_path='rigid_body_constraint.motor_ang_y_velocity', frame=0)
hook_constraint.rigid_body_constraint.motor_ang_y_velocity = 0.0
hook_constraint.keyframe_insert(data_path='rigid_body_constraint.motor_ang_y_velocity', frame=200)

# Arm motor: active frames 200-350 (rotate 90°)
arm_constraint.rigid_body_constraint.motor_ang_z_velocity = 0.0
arm_constraint.keyframe_insert(data_path='rigid_body_constraint.motor_ang_z_velocity', frame=0)
arm_constraint.rigid_body_constraint.motor_ang_z_velocity = arm_motor_v
arm_constraint.keyframe_insert(data_path='rigid_body_constraint.motor_ang_z_velocity', frame=200)
arm_constraint.rigid_body_constraint.motor_ang_z_velocity = 0.0
arm_constraint.keyframe_insert(data_path='rigid_body_constraint.motor_ang_z_velocity', frame=350)

# Enable load constraint at frame 50 (after hook lowers)
load_constraint.rigid_body_constraint.enabled = False
load_constraint.keyframe_insert(data_path='rigid_body_constraint.enabled', frame=0)
load_constraint.rigid_body_constraint.enabled = True
load_constraint.keyframe_insert(data_path='rigid_body_constraint.enabled', frame=50)