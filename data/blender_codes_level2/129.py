import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
col_dim = column_dim = (0.5, 0.5, 2.5)
col_loc = column_loc = (0.0, 0.0, 1.25)
jib_dim = jib_dim = (3.5, 0.3, 0.3)
jib_loc = jib_loc = (0.0, 2.0, 2.4)
cnt_dim = counter_dim = (0.8, 0.8, 0.8)
cnt_loc = counter_loc = (0.0, -0.65, 2.5)
hook_rad = hook_radius = 0.1
hook_dep = hook_depth = 0.5
hook_loc = hook_loc = (0.0, 3.75, 2.0)
load_mass = load_mass = 450.0
cnt_mass = counter_mass = 2423.0
motor_vel = hinge_motor_velocity = 0.5
frames = simulation_frames = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.name = "SupportColumn"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create Jib Beam
bpy.ops.mesh.primitive_cube_add(size=1, location=jib_loc)
jib = bpy.context.active_object
jib.name = "JibBeam"
jib.scale = jib_dim
bpy.ops.rigidbody.object_add()
jib.rigid_body.type = 'PASSIVE'
jib.rigid_body.collision_shape = 'BOX'

# Create Counterweight
bpy.ops.mesh.primitive_cube_add(size=1, location=cnt_loc)
counter = bpy.context.active_object
counter.name = "Counterweight"
counter.scale = cnt_dim
bpy.ops.rigidbody.object_add()
counter.rigid_body.type = 'PASSIVE'
counter.rigid_body.mass = cnt_mass
counter.rigid_body.collision_shape = 'BOX'

# Create Load Hook (Cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=hook_rad,
    depth=hook_dep,
    location=hook_loc,
    rotation=(0, 0, 0)
)
hook = bpy.context.active_object
hook.name = "LoadHook"
bpy.ops.rigidbody.object_add()
hook.rigid_body.type = 'ACTIVE'
hook.rigid_body.mass = load_mass
hook.rigid_body.collision_shape = 'MESH'

# Add Fixed Constraint between Column and Jib
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 2.5))
constraint_fixed = bpy.context.active_object
constraint_fixed.name = "FixedConstraint_JibColumn"
bpy.ops.rigidbody.constraint_add()
constraint_fixed.rigid_body_constraint.type = 'FIXED'
constraint_fixed.rigid_body_constraint.object1 = column
constraint_fixed.rigid_body_constraint.object2 = jib

# Add Fixed Constraint between Column and Counterweight
bpy.ops.object.empty_add(type='PLAIN_AXES', location=cnt_loc)
constraint_counter = bpy.context.active_object
constraint_counter.name = "FixedConstraint_Counterweight"
bpy.ops.rigidbody.constraint_add()
constraint_counter.rigid_body_constraint.type = 'FIXED'
constraint_counter.rigid_body_constraint.object1 = column
constraint_counter.rigid_body_constraint.object2 = counter

# Add Hinge Constraint between Jib and Hook
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 3.75, 2.4))
constraint_hinge = bpy.context.active_object
constraint_hinge.name = "HingeConstraint_Hook"
bpy.ops.rigidbody.constraint_add()
constraint_hinge.rigid_body_constraint.type = 'HINGE'
constraint_hinge.rigid_body_constraint.object1 = jib
constraint_hinge.rigid_body_constraint.object2 = hook
constraint_hinge.rigid_body_constraint.use_limit_ang_z = True
constraint_hinge.rigid_body_constraint.limit_ang_z_lower = -1.57  # -90 deg
constraint_hinge.rigid_body_constraint.limit_ang_z_upper = 0.0    # 0 deg
constraint_hinge.rigid_body_constraint.use_motor_ang = True
constraint_hinge.rigid_body_constraint.motor_ang_target_velocity = motor_vel
constraint_hinge.rigid_body_constraint.motor_ang_max_impulse = 10000.0

# Set simulation end frame
bpy.context.scene.frame_end = frames

# Optional: Set gravity to standard 9.81 m/s² (Blender default is 9.8)
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)