import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
column_dim = (0.5, 0.5, 4.0)
column_loc = (0.0, 0.0, 2.25)
boom_dim = (5.0, 0.5, 0.5)
boom_loc = (2.5, 0.0, 4.25)
hinge_pivot_world = (0.0, 0.0, 4.25)
angular_velocity_target = 0.785398  # π/4 rad/s

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "SupportColumn"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create Boom Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=boom_loc)
boom = bpy.context.active_object
boom.name = "BoomArm"
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.collision_shape = 'BOX'

# Add Fixed Constraint between Base and Column
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Base_Column"
fixed_constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
con = fixed_constraint.rigid_body_constraint
con.type = 'FIXED'
con.object1 = base
con.object2 = column

# Add Hinge Constraint between Column and Boom
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot_world)
hinge_constraint = bpy.context.active_object
hinge_constraint.name = "Hinge_Column_Boom"
hinge_constraint.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
con = hinge_constraint.rigid_body_constraint
con.type = 'HINGE'
con.object1 = column
con.object2 = boom
con.use_limit_z = False  # Allow full rotation
con.use_motor_z = True
con.motor_angular_target_velocity_z = angular_velocity_target
con.motor_max_impulse_z = 10.0  # Reasonable torque

# Set hinge axis to global Z
con.axis_primary = 'Z'
con.axis_secondary = 'Y'

# Set collision margins (optional but good practice)
for obj in [base, column, boom]:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.04

# Ensure rigid body world exists
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

# Set gravity to default (Z downward)
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Frame range for animation (optional)
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250