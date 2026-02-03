import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
arm_dim = (2.0, 0.2, 0.2)
arm_loc = (1.0, 0.0, 0.35)
proj_dim = (0.3, 0.3, 0.3)
proj_loc = (2.0, 0.0, 0.6)
hinge_pivot = (0.0, 0.0, 0.35)
hinge_axis = (0.0, 1.0, 0.0)
motor_vel = 10.0
sim_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Add fixed constraint to ground (via empty anchor)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=base_loc)
anchor = bpy.context.active_object
anchor.name = "Anchor"
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Fixed_Base"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = base
constraint.rigid_body_constraint.object2 = anchor

# Create catapult arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Catapult_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Create projectile cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=proj_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = proj_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'

# Create hinge constraint between arm and base
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge = bpy.context.active_object
hinge.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge_constraint = hinge.rigid_body_constraint
hinge_constraint.type = 'HINGE'
hinge_constraint.object1 = arm
hinge_constraint.object2 = base
hinge_constraint.pivot_x = hinge_pivot[0]
hinge_constraint.pivot_y = hinge_pivot[1]
hinge_constraint.pivot_z = hinge_pivot[2]
hinge_constraint.axis_x = hinge_axis[0]
hinge_constraint.axis_y = hinge_axis[1]
hinge_constraint.axis_z = hinge_axis[2]

# Enable motor with target velocity
hinge_constraint.use_motor = True
hinge_constraint.motor_type = 'VELOCITY'
hinge_constraint.motor_velocity = motor_vel

# Configure simulation duration
bpy.context.scene.frame_end = sim_frames

# Optional: Set rigid body world substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Catapult assembly complete. Simulation ready.")