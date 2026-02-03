import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
arm_dim = (0.2, 2.0, 0.2)
arm_loc = (0.0, 2.5, 0.25)
block_dim = (0.8, 0.8, 0.8)
block_loc = (0.0, 3.5, 0.75)
pivot_loc = (0.0, 1.5, 0.25)
hinge_axis = (0.0, 1.0, 0.0)
motor_velocity = 15.0
motor_duration = 10
motor_torque = 1000.0
arm_mass = 5.0
block_mass = 100.0
collision_margin = 0.04
sim_frames = 200

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.collection = None  # Use default

# 1. BASE PLATFORM (Passive)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_margin = collision_margin
base.rigid_body.mass = 0.0  # Infinite mass

# 2. CATAPULT ARM (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "CatapultArm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_margin = collision_margin
arm.rigid_body.mass = arm_mass
arm.rigid_body.linear_damping = 0.1
arm.rigid_body.angular_damping = 0.1

# 3. HEAVY BLOCK (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=block_loc)
block = bpy.context.active_object
block.name = "HeavyBlock"
block.scale = block_dim
bpy.ops.rigidbody.object_add()
block.rigid_body.type = 'ACTIVE'
block.rigid_body.collision_margin = collision_margin
block.rigid_body.mass = block_mass
block.rigid_body.linear_damping = 0.05
block.rigid_body.angular_damping = 0.05

# 4. CONSTRAINTS
# 4a. Hinge between Base and Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_loc)
hinge_empty = bpy.context.active_object
hinge_empty.name = "HingeConstraint"
bpy.ops.rigidbody.constraint_add()
hinge_empty.rigid_body_constraint.type = 'HINGE'
hinge_empty.rigid_body_constraint.object1 = base
hinge_empty.rigid_body_constraint.object2 = arm
hinge_empty.rigid_body_constraint.use_limit_ang_z = True
hinge_empty.rigid_body_constraint.limit_ang_z_lower = 0.0
hinge_empty.rigid_body_constraint.limit_ang_z_upper = math.radians(120.0)
hinge_empty.rigid_body_constraint.use_motor_ang = True
hinge_empty.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
hinge_empty.rigid_body_constraint.motor_ang_max_torque = motor_torque

# 4b. Fixed constraint between Arm and Block
bpy.ops.object.empty_add(type='PLAIN_AXES', location=block_loc)
fixed_empty = bpy.context.active_object
fixed_empty.name = "FixedConstraint"
bpy.ops.rigidbody.constraint_add()
fixed_empty.rigid_body_constraint.type = 'FIXED'
fixed_empty.rigid_body_constraint.object1 = arm
fixed_empty.rigid_body_constraint.object2 = block
fixed_empty.rigid_body_constraint.use_breaking = True
fixed_empty.rigid_body_constraint.breaking_threshold = 5000.0

# 5. MOTOR ANIMATION (velocity for 10 frames then 0)
hinge_empty.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
hinge_empty.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity", frame=1)
hinge_empty.rigid_body_constraint.motor_ang_target_velocity = 0.0
hinge_empty.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity", frame=motor_duration+1)

# 6. SCENE SETUP
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Catapult mechanism constructed. Simulation ready.")