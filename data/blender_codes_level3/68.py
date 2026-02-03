import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
p_dim = (3.0, 3.0, 0.5)
p_loc_local = mathutils.Vector((0.0, 0.0, 0.25))
c_dim = (0.5, 0.5, 2.0)
c_loc_local = mathutils.Vector((0.0, 0.0, 1.5))
a_dim = (4.0, 0.3, 0.3)
a_loc_local = mathutils.Vector((2.0, 0.0, 2.5))
proj_dim = (0.5, 0.5, 0.5)
proj_loc_local = mathutils.Vector((4.0, 0.0, 2.5))
trans = mathutils.Vector((-4.0, 0.0, 0.0))
hinge_pivot = mathutils.Vector((-4.0, 0.0, 2.5))
motor_vel = 10.0
break_force = 50.0

# Compute world locations
p_loc = p_loc_local + trans
c_loc = c_loc_local + trans
a_loc = a_loc_local + trans
proj_loc = proj_loc_local + trans

# 1. Base Platform (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=p_loc)
platform = bpy.context.active_object
platform.scale = p_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.name = "BasePlatform"

# 2. Support Column (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=c_loc)
column = bpy.context.active_object
column.scale = c_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.name = "SupportColumn"

# 3. Launch Arm (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=a_loc)
arm = bpy.context.active_object
arm.scale = a_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.name = "LaunchArm"

# 4. Projectile (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=proj_loc)
projectile = bpy.context.active_object
projectile.scale = proj_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.name = "Projectile"

# 5. Constraints
# 5a. Fixed constraint between Platform and Column
bpy.ops.rigidbody.constraint_add()
fixed1 = bpy.context.active_object
fixed1.rigid_body_constraint.type = 'FIXED'
fixed1.rigid_body_constraint.object1 = platform
fixed1.rigid_body_constraint.object2 = column
fixed1.name = "Platform_Column_Fixed"

# 5b. Hinge constraint between Column and Arm (motorized)
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = column
hinge.rigid_body_constraint.object2 = arm
hinge.location = hinge_pivot
hinge.rigid_body_constraint.use_limit_z = False
hinge.rigid_body_constraint.use_motor = True
hinge.rigid_body_constraint.motor_angular_target_velocity = motor_vel
hinge.rigid_body_constraint.motor_max_impulse = 1000.0  # High torque for rapid acceleration
hinge.name = "Arm_Hinge_Motor"

# 5c. Fixed constraint between Arm and Projectile (breakable)
bpy.ops.rigidbody.constraint_add()
fixed2 = bpy.context.active_object
fixed2.rigid_body_constraint.type = 'FIXED'
fixed2.rigid_body_constraint.object1 = arm
fixed2.rigid_body_constraint.object2 = projectile
fixed2.rigid_body_constraint.use_breaking = True
fixed2.rigid_body_constraint.breaking_threshold = break_force
fixed2.name = "Arm_Projectile_Fixed_Breakable"