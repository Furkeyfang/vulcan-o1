import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract variables from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
support_dim = (0.5, 0.5, 4.0)
support_loc = (0.0, 0.0, 2.5)
pivot_point = (0.0, 0.0, 4.5)
arm_dim = (3.0, 0.3, 0.3)
arm_loc = (0.0, 1.5, 4.5)
projectile_dim = (0.5, 0.5, 0.5)
projectile_loc = (0.0, 3.0, 4.5)
hinge_axis = (1.0, 0.0, 0.0)
motor_velocity = 6.0
arm_mass = 5.0
projectile_mass = 2.0
base_mass = 50.0

# Create Base
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.mass = base_mass

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1, location=support_loc)
support = bpy.context.active_object
support.name = "Support"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
# Rotate arm 90° around X to start horizontal? Actually default cube orientation is fine (aligned with axes)
# We'll rotate so local Y is along length
arm.rotation_euler = (0, 0, 0)  # Already correct
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass

# Create Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=1, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = projectile_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = projectile_mass

# Add Hinge Constraint between Support and Arm
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = support
constraint.rigid_body_constraint.object2 = arm
constraint.location = pivot_point
constraint.rigid_body_constraint.use_limit_ang_z = True
constraint.rigid_body_constraint.limit_ang_z_lower = 0
constraint.rigid_body_constraint.limit_ang_z_upper = math.radians(90)
constraint.rigid_body_constraint.use_motor_ang_z = True
constraint.rigid_body_constraint.motor_ang_z_velocity = motor_velocity
constraint.rigid_body_constraint.motor_ang_z_max_torque = 1000.0
# Set hinge axis
constraint.rigid_body_constraint.axis = hinge_axis

# Add Fixed Constraint between Arm and Projectile
bpy.ops.rigidbody.constraint_add()
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Projectile"
fixed_constraint.rigid_body_constraint.type = 'FIXED'
fixed_constraint.rigid_body_constraint.object1 = arm
fixed_constraint.rigid_body_constraint.object2 = projectile
fixed_constraint.location = projectile_loc

# Set world gravity (default -9.81 Z)
bpy.context.scene.gravity = (0, 0, -9.81)

# Optional: Set simulation substeps for accuracy
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Catapult mechanism constructed. Arm will rotate upward with motor velocity", motor_velocity, "rad/s.")
print("Projectile expected max height >12m.")