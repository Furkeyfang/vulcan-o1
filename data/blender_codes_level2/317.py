import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (1.0, 1.0, 10.0)
base_loc = (0.0, 0.0, 0.0)

# Arm parameters
arm_len = [3.0, 4.0, 6.0]
arm_cross = [0.3, 0.4, 0.5]
arm_height = [8.0, 6.0, 4.0]
arm_pos = [(1.5, 0.0, 8.0), (2.0, 0.0, 6.0), (3.0, 0.0, 4.0)]

# Load parameters
load_size = [0.5, 0.6, 0.7]
load_mass = [200.0, 300.0, 400.0]
load_pos = [(3.0, 0.0, 8.0), (4.0, 0.0, 6.0), (6.0, 0.0, 4.0)]

motor_vel = 1.0

# Create base (static anchor)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Crane_Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create arms and loads
for i in range(3):
    # Create arm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_pos[i])
    arm = bpy.context.active_object
    arm.name = f"Arm_{i+1}"
    arm.scale = (arm_len[i], arm_cross[i], arm_cross[i])
    bpy.ops.rigidbody.object_add()
    arm.rigid_body.mass = 50.0  # Default arm mass
    
    # Create hinge constraint between base and arm
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{i+1}"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = base
    constraint.rigid_body_constraint.object2 = arm
    
    # Position hinge at attachment point
    constraint.location = (0.0, 0.0, arm_height[i])
    
    # Set hinge axis to Y (for rotation in XZ plane)
    constraint.rigid_body_constraint.use_angular_friction = True
    constraint.rigid_body_constraint.use_limit_ang_z = False
    
    # Configure as motor
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_vel
    constraint.rigid_body_constraint.motor_ang_max_torque = 1000.0
    
    # Create load
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos[i])
    load = bpy.context.active_object
    load.name = f"Load_{i+1}"
    load.scale = (load_size[i], load_size[i], load_size[i])
    bpy.ops.rigidbody.object_add()
    load.rigid_body.mass = load_mass[i]
    
    # Create fixed constraint between arm and load
    bpy.ops.rigidbody.constraint_add()
    fixed = bpy.context.active_object
    fixed.name = f"Fixed_{i+1}"
    fixed.rigid_body_constraint.type = 'FIXED'
    fixed.rigid_body_constraint.object1 = arm
    fixed.rigid_body_constraint.object2 = load
    fixed.location = load_pos[i]

# Ensure physics world is active
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Set gravity (default is -9.81 Z)
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Set simulation substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50