import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
base_dim = (2.0, 2.0, 0.2)
base_loc = (0.0, 0.0, 0.1)
column_dim = (0.2, 0.2, 1.5)
column_loc = (0.0, 0.0, 0.95)
hinge_pivot = (0.0, 0.0, 1.7)
arm_dim = (0.15, 0.15, 2.0)
arm_loaded_rot = 45.0
holder_dim = (0.3, 0.3, 0.3)
holder_offset = (0.0, 0.0, 2.0)
counterweight_dim = (0.4, 0.4, 0.4)
counterweight_offset = (0.0, 0.0, 0.5)
motor_velocity = -10.0
projectile_radius = 0.1

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create Arm (centered at hinge pivot)
bpy.ops.mesh.primitive_cube_add(size=1, location=hinge_pivot)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
arm.rotation_euler = (0.0, math.radians(arm_loaded_rot), 0.0)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Create Projectile Holder (fixed to arm end)
holder_loc = (
    hinge_pivot[0] + holder_offset[0],
    hinge_pivot[1] + holder_offset[1],
    hinge_pivot[2] + holder_offset[2]
)
bpy.ops.mesh.primitive_cube_add(size=1, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Holder"
holder.scale = holder_dim
holder.parent = arm
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'PASSIVE'

# Create Counterweight
counterweight_loc = (
    hinge_pivot[0] + counterweight_offset[0],
    hinge_pivot[1] + counterweight_offset[1],
    hinge_pivot[2] + counterweight_offset[2]
)
bpy.ops.mesh.primitive_cube_add(size=1, location=counterweight_loc)
counterweight = bpy.context.active_object
counterweight.name = "Counterweight"
counterweight.scale = counterweight_dim
counterweight.parent = arm
bpy.ops.rigidbody.object_add()
counterweight.rigid_body.type = 'PASSIVE'

# Create Projectile Sphere
projectile_loc = holder_loc
bpy.ops.mesh.primitive_uv_sphere_add(radius=projectile_radius, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = 0.1

# Create Hinge Constraint between Arm and Column
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
empty = bpy.context.active_object
empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = arm
constraint.object2 = column
constraint.use_motor = True
constraint.motor_angular_target_velocity = motor_velocity
constraint.use_limit_angular = False

# Set simulation frame range
bpy.context.scene.frame_end = 100