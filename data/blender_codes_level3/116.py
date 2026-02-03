import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
column_dim = (0.5, 0.5, 4.0)
column_loc = (0.0, 0.0, 2.25)
boom_dim = (5.0, 0.5, 0.5)
boom_loc = (2.5, 0.0, 4.25)
hinge_pivot_world = (0.0, 0.0, 0.0)
motor_velocity_target = 2.0
simulation_frames = 500
rigidbody_damping = 0.1

# Ensure we have a scene with rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.enabled = True
base.rigid_body.collision_shape = 'BOX'

# Create Vertical Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.enabled = True
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.linear_damping = rigidbody_damping
column.rigid_body.angular_damping = rigidbody_damping

# Create Boom Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=boom_loc)
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.enabled = True
boom.rigid_body.collision_shape = 'BOX'
boom.rigid_body.linear_damping = rigidbody_damping
boom.rigid_body.angular_damping = rigidbody_damping

# Add Hinge Constraint between Base and Column
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.name = "Hinge_Base_Column"
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = base
hinge.rigid_body_constraint.object2 = column
# Set pivot in world coordinates, then convert to local for each object
hinge.location = hinge_pivot_world
# Compute local pivots: for base (at origin), pivot is (0,0,0) in its local space
# For column, transform world pivot into column's local coordinates
column_local_pivot = column.matrix_world.inverted() @ mathutils.Vector(hinge_pivot_world)
hinge.rigid_body_constraint.pivot_type = 'PIVOT_XYZ'
hinge.rigid_body_constraint.use_limits_x = False
hinge.rigid_body_constraint.use_limits_y = False
hinge.rigid_body_constraint.use_limits_z = False
hinge.rigid_body_constraint.use_motor_x = False
hinge.rigid_body_constraint.use_motor_y = False
hinge.rigid_body_constraint.use_motor_z = True
hinge.rigid_body_constraint.motor_lin_target_velocity = 0.0
hinge.rigid_body_constraint.motor_ang_target_velocity = motor_velocity_target
hinge.rigid_body_constraint.use_motor_lin = False
hinge.rigid_body_constraint.use_motor_ang = True

# Add Fixed Constraint between Column and Boom
bpy.ops.rigidbody.constraint_add()
fixed = bpy.context.active_object
fixed.name = "Fixed_Column_Boom"
fixed.rigid_body_constraint.type = 'FIXED'
fixed.rigid_body_constraint.object1 = column
fixed.rigid_body_constraint.object2 = boom
# Place constraint at the attachment point: top center of column
attachment_world = (0.0, 0.0, 4.25)
fixed.location = attachment_world
# No need to set pivots explicitly for FIXED type in Blender 3.6+

# Set simulation end frame
bpy.context.scene.frame_end = simulation_frames

# Optional: Add a ground plane for visual reference (not required for physics)
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0,0,-0.5))
ground = bpy.context.active_object
ground.name = "Ground"
ground.rigid_body.type = 'PASSIVE'