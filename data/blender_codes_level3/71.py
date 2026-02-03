import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract all parameters
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
col_dim = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.5)
arm_dim = (3.0, 0.3, 0.3)
arm_loc = (1.5, 0.0, 2.5)
holder_dim = (0.5, 0.5, 0.5)
holder_loc = (3.0, 0.0, 2.5)
proj_radius = 0.2
proj_loc = (3.0, 0.0, 2.5)
hinge1_pivot = (0.0, 0.0, 2.5)
hinge1_axis = (0.0, 0.0, 1.0)
hinge2_pivot = (3.0, 0.0, 2.5)
hinge2_axis = (0.0, 0.0, 1.0)
motor1_velocity = 6.0
motor2_velocity = -8.0
simulation_frames = 200

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# 1. BASE PLATFORM (Passive)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. SUPPORT COLUMN (Active, fixed to base)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'

# Fixed constraint between Base and Column
bpy.ops.rigidbody.constraint_add()
fix1 = bpy.context.active_object
fix1.name = "Fix_Base_Column"
fix1.rigid_body_constraint.type = 'FIXED'
fix1.rigid_body_constraint.object1 = base
fix1.rigid_body_constraint.object2 = column

# 3. HORIZONTAL ARM (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Hinge constraint between Column and Arm (Primary)
bpy.ops.rigidbody.constraint_add()
hinge1 = bpy.context.active_object
hinge1.name = "Hinge_Arm_Column"
hinge1.rigid_body_constraint.type = 'HINGE'
hinge1.rigid_body_constraint.object1 = column
hinge1.rigid_body_constraint.object2 = arm
hinge1.location = hinge1_pivot
hinge1.rigid_body_constraint.pivot_type = 'CUSTOM'
hinge1.rigid_body_constraint.use_limit_z = False
hinge1.rigid_body_constraint.use_motor_z = True
hinge1.rigid_body_constraint.motor_velocity_z = motor1_velocity

# 4. PROJECTILE HOLDER (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Holder"
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'

# Hinge constraint between Arm and Holder (Secondary)
bpy.ops.rigidbody.constraint_add()
hinge2 = bpy.context.active_object
hinge2.name = "Hinge_Holder_Arm"
hinge2.rigid_body_constraint.type = 'HINGE'
hinge2.rigid_body_constraint.object1 = arm
hinge2.rigid_body_constraint.object2 = holder
hinge2.location = hinge2_pivot
hinge2.rigid_body_constraint.pivot_type = 'CUSTOM'
hinge2.rigid_body_constraint.use_limit_z = False
hinge2.rigidbody_constraint.use_motor_z = True
hinge2.rigidbody_constraint.motor_velocity_z = motor2_velocity

# 5. SPHERICAL PROJECTILE (Active)
bpy.ops.mesh.primitive_uv_sphere_add(radius=proj_radius, location=proj_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'SPHERE'

# Parent projectile to holder for initial positioning (will break on simulation)
projectile.parent = holder
projectile.matrix_parent_inverse = holder.matrix_world.inverted()

# Set simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Keyframe motors to start at frame 1
hinge1.rigid_body_constraint.motor_velocity_z = motor1_velocity
hinge1.keyframe_insert(data_path="rigid_body_constraint.motor_velocity_z", frame=1)
hinge2.rigid_body_constraint.motor_velocity_z = motor2_velocity
hinge2.keyframe_insert(data_path="rigid_body_constraint.motor_velocity_z", frame=1)