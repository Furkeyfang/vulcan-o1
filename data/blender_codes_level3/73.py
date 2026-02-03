import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define parameters from summary
base_dim = (2.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.15)
arm_dim = (0.2, 2.0, 0.2)
arm_loc = (0.0, 1.0, 0.4)
proj_radius = 0.15
proj_height = 0.3
proj_loc = (0.0, 2.0, 0.4)
hinge_pivot = (0.0, 0.0, 0.4)
motor_velocity = 9.0
simulation_frames = 100

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)

# Create Base
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 1.0

# Create Projectile
bpy.ops.mesh.primitive_cylinder_add(
    radius=proj_radius, 
    depth=proj_height,
    location=proj_loc
)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'CYLINDER'
projectile.rigid_body.mass = 0.5

# Create Fixed Constraint between Base and World (simulated by making base passive)
# Base is already passive and won't move

# Create Hinge Constraint between Base and Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge_empty.rigid_body_constraint.type = 'HINGE'
hinge_empty.rigid_body_constraint.object1 = base
hinge_empty.rigid_body_constraint.object2 = arm
hinge_empty.rigid_body_constraint.use_limit_ang_z = True
hinge_empty.rigid_body_constraint.limit_ang_z_lower = -math.radians(360)
hinge_empty.rigid_body_constraint.limit_ang_z_upper = math.radians(360)
hinge_empty.rigid_body_constraint.use_motor_ang = True
hinge_empty.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
hinge_empty.rigid_body_constraint.motor_ang_max_impulse = 100.0

# Create Fixed Constraint between Arm and Projectile
bpy.ops.object.empty_add(type='PLAIN_AXES', location=proj_loc)
fixed_empty = bpy.context.active_object
fixed_empty.name = "Arm_Projectile_Fixed"
bpy.ops.rigidbody.constraint_add()
fixed_empty.rigid_body_constraint.type = 'FIXED'
fixed_empty.rigid_body_constraint.object1 = arm
fixed_empty.rigid_body_constraint.object2 = projectile
# Set breaking threshold to simulate launch
fixed_empty.rigid_body_constraint.use_breaking = True
fixed_empty.rigid_body_constraint.breaking_threshold = 50.0

# Set simulation frames
bpy.context.scene.frame_end = simulation_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print("Launcher mechanism constructed. Simulation ready for 100 frames.")
print(f"Projectile starting position: {proj_loc}")
print(f"Target horizontal displacement: >18 meters")