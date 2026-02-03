import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.3)
base_loc = (0.0, 0.0, 0.15)
base_mass = 100.0
arm_dim = (0.2, 2.0, 0.2)
arm_loc = (0.0, 1.0, 0.3)
arm_mass = 5.0
hinge_pivot = (0.0, 0.0, 0.3)
hinge_axis = (1.0, 0.0, 0.0)
motor_velocity = 6.0
motor_max_impulse = 1000.0
projectile_radius = 0.15
projectile_loc = (0.0, 2.0, 0.55)
projectile_mass = 10.0
restitution = 0.9
friction = 0.1
fps = 60
frame_end = 100
gravity = -9.8

# Set scene properties for physics simulation
scene = bpy.context.scene
scene.frame_end = frame_end
scene.render.fps = fps
if scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
scene.rigidbody_world.gravity = (0, 0, gravity)
scene.rigidbody_world.substeps_per_frame = 10
scene.rigidbody_world.solver_iterations = 10

# Create base platform (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.mass = base_mass
base.rigid_body.restitution = restitution
base.rigid_body.friction = friction
base.rigid_body.collision_shape = 'BOX'

# Create catapult arm (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass
arm.rigid_body.restitution = restitution
arm.rigid_body.friction = friction
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.linear_damping = 0.1
arm.rigid_body.angular_damping = 0.1

# Create projectile sphere (active rigid body)
bpy.ops.mesh.primitive_uv_sphere_add(radius=projectile_radius, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = projectile_mass
projectile.rigid_body.restitution = restitution
projectile.rigid_body.friction = friction
projectile.rigid_body.collision_shape = 'SPHERE'
projectile.rigid_body.linear_damping = 0.05
projectile.rigid_body.angular_damping = 0.05

# Add hinge constraint between base and arm
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Motor"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = base
constraint.rigid_body_constraint.object2 = arm
constraint.rigid_body_constraint.pivot_type = 'CUSTOM'
constraint.location = hinge_pivot
constraint.rigid_body_constraint.use_limit_ang_z = False
constraint.rigid_body_constraint.use_motor_ang = True
constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
constraint.rigid_body_constraint.motor_ang_max_impulse = motor_max_impulse

# Set hinge axis rotation to align with global X
constraint.rotation_mode = 'XYZ'
constraint.rotation_euler = (0.0, 0.0, 0.0)  # Default orientation already aligns with world axes

# Verify that the constraint pivot matches the hinge point
constraint.rigid_body_constraint.pivot_x = hinge_pivot[0]
constraint.rigid_body_constraint.pivot_y = hinge_pivot[1]
constraint.rigid_body_constraint.pivot_z = hinge_pivot[2]
constraint.rigid_body_constraint.axis_x = hinge_axis[0]
constraint.rigid_body_constraint.axis_y = hinge_axis[1]
constraint.rigid_body_constraint.axis_z = hinge_axis[2]

# Optional: Bake the simulation to keyframes for verification (headless compatible)
# Note: Baking requires a rigid body world and is done via operators that work in background mode.
bpy.ops.ptcache.bake_all(bake=True)