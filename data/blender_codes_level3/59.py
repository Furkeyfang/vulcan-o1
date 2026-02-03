import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.3)
base_loc = (0.0, 0.0, 0.15)

arm_dim = (2.0, 0.2, 0.2)
arm_loc = (1.0, 1.5, 0.3)

projectile_dim = 0.3
projectile_loc = (2.0, 1.5, 0.55)

pivot_loc = (0.0, 1.5, 0.3)
hinge_axis = (0.0, 1.0, 0.0)
motor_velocity = 10.0

sim_frames = 150
frame_rate = 60

# Set scene properties
scene = bpy.context.scene
scene.frame_end = sim_frames
scene.render.fps = frame_rate
scene.gravity = (0.0, 0.0, -9.81)  # Standard gravity

# Create base platform (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create catapult arm (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Catapult_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 2.0  # Reasonable mass for 2m beam

# Create projectile (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = (projectile_dim, projectile_dim, projectile_dim)
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = 0.5  # Light projectile for launch

# Create hinge constraint at pivot point
bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_loc)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = base
constraint.object2 = arm
constraint.pivot_type = 'CUSTOM'
constraint.use_limit_angle = False
constraint.use_motor = True
constraint.motor_angular_velocity = motor_velocity
constraint.motor_max_impulse = 100.0  # Sufficient torque

# Align hinge axis to world Y
constraint_empty.rotation_euler = (0.0, 0.0, 0.0)  # Y-axis already global Y

# Set initial arm rotation to horizontal (0° about Y)
arm.rotation_euler = (0.0, 0.0, 0.0)

# Keyframe motor activation at frame 1
constraint.motor_angular_velocity = 0.0
constraint.keyframe_insert(data_path="motor_angular_velocity", frame=1)
constraint.motor_angular_velocity = motor_velocity
constraint.keyframe_insert(data_path="motor_angular_velocity", frame=5)

# Enable rigid body simulation
scene.rigidbody_world.enabled = True

# Optional: Add floor for realism
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, -0.1))
floor = bpy.context.active_object
floor.name = "Ground"
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'

print("Catapult mechanism created. Simulation will run for", sim_frames, "frames.")
print("Expected projectile horizontal displacement > 9 meters from starting X=2.0")