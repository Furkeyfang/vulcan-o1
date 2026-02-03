import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
base_dim = (6.0, 4.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
support_dim = (0.5, 0.5, 2.0)
support_loc = (0.0, -2.0, 0.25)
arm_dim = (4.0, 0.3, 0.3)
arm_loc = (0.0, 0.0, 2.25)
bucket_dim = (1.0, 1.0, 0.5)
bucket_loc = (0.0, -2.0, 1.85)
holder_dim = (0.3, 0.3, 0.2)
holder_loc = (0.0, 2.0, 2.5)
hinge_pivot = (0.0, -2.0, 2.25)
motor_velocity = -8.0

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1, location=support_loc)
support = bpy.context.active_object
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'

# Create Throwing Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 2.0

# Create Counterweight Bucket
bpy.ops.mesh.primitive_cube_add(size=1, location=bucket_loc)
bucket = bpy.context.active_object
bucket.scale = bucket_dim
bpy.ops.rigidbody.object_add()
bucket.rigid_body.type = 'ACTIVE'
bucket.rigid_body.collision_shape = 'CONVEX_HULL'
bucket.rigid_body.mass = 50.0  # Heavy counterweight

# Create Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=1, location=holder_loc)
holder = bpy.context.active_object
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.collision_shape = 'BOX'
holder.rigid_body.mass = 0.5

# Create Fixed Constraint: Base ↔ Support
bpy.ops.rigidbody.constraint_add()
fixed1 = bpy.context.active_object
fixed1.rigid_body_constraint.type = 'FIXED'
fixed1.rigid_body_constraint.object1 = base
fixed1.rigid_body_constraint.object2 = support

# Create Fixed Constraint: Arm ↔ Bucket
bpy.ops.rigidbody.constraint_add()
fixed2 = bpy.context.active_object
fixed2.rigid_body_constraint.type = 'FIXED'
fixed2.rigid_body_constraint.object1 = arm
fixed2.rigid_body_constraint.object2 = bucket
fixed2.rigid_body_constraint.spring_stiffness = 1000  # Stiff connection

# Create Fixed Constraint: Arm ↔ Holder
bpy.ops.rigidbody.constraint_add()
fixed3 = bpy.context.active_object
fixed3.rigid_body_constraint.type = 'FIXED'
fixed3.rigid_body_constraint.object1 = arm
fixed3.rigid_body_constraint.object2 = holder
fixed3.rigid_body_constraint.spring_stiffness = 1000

# Create Hinge Constraint: Support ↔ Arm
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = support
hinge.rigid_body_constraint.object2 = arm
hinge.location = hinge_pivot
hinge.rotation_euler = (0.0, 0.0, 0.0)  # Y-axis is default hinge axis
hinge.rigid_body_constraint.use_motor = True
hinge.rigid_body_constraint.motor_angular_target_velocity = motor_velocity
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = -1.57  # -90 degrees
hinge.rigid_body_constraint.limit_ang_z_upper = 0.0    # Start horizontal