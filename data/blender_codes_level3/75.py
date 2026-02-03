import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (6.0, 4.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
arm_dim = (5.0, 0.3, 0.3)
arm_loc = (3.0, 0.0, 2.75)
holder_dim = (0.5, 0.5, 0.5)
holder_loc = (3.0, 0.0, 5.25)
pivot_loc = (3.0, 0.0, 0.25)
ground_loc = (0.0, 0.0, -1.0)
motor_velocity = 10.0
base_mass = 10.0
arm_mass = 2.0
projectile_mass = 5.0
friction_coeff = 0.1
simulation_frames = 100

# Create ground plane (static)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = friction_coeff

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = (base_dim[0]/2, base_dim[1]/2, base_dim[2]/2)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'ACTIVE'
base.rigid_body.mass = base_mass
base.rigid_body.friction = friction_coeff

# Create catapult arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_dim[0]/2, arm_dim[1]/2, arm_dim[2]/2)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass

# Create projectile holder
bpy.ops.mesh.primitive_cube_add(size=1.0, location=holder_loc)
holder = bpy.context.active_object
holder.name = "ProjectileHolder"
holder.scale = (holder_dim[0]/2, holder_dim[1]/2, holder_dim[2]/2)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.mass = projectile_mass

# Create hinge constraint between base and arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_loc)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Pivot"

bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Constraint"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = base
constraint.rigid_body_constraint.object2 = arm
constraint.rigid_body_constraint.use_breaking = False
constraint.rigid_body_constraint.use_motor = True
constraint.rigid_body_constraint.motor_lin_target_velocity = 0.0
constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
constraint.location = pivot_loc
constraint.rotation_euler = (0.0, 0.0, 0.0)  # Y-axis hinge

# Create fixed constraint between arm and projectile holder
bpy.ops.rigidbody.constraint_add()
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Constraint"
fixed_constraint.rigid_body_constraint.type = 'FIXED'
fixed_constraint.rigid_body_constraint.object1 = arm
fixed_constraint.rigid_body_constraint.object2 = holder
fixed_constraint.rigid_body_constraint.use_breaking = False

# Set up simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Position the hinge pivot correctly relative to both objects
# The constraint will use the empty's location as pivot point
constraint.parent = hinge_empty
constraint.matrix_parent_inverse = hinge_empty.matrix_world.inverted()

print(f"Catapult constructed. Base starts at {base_loc}")
print(f"Motor velocity: {motor_velocity} rad/s")
print(f"Simulation will run for {simulation_frames} frames")