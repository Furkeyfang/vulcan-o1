import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
# Base
base_dim = (3.0, 2.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

# Arm
arm_dim = (0.2, 2.5, 0.2)
arm_loc = (0.0, 0.0, 0.6)

# Counterweight
counterweight_dim = 1.0
counterweight_loc = (0.0, -1.25, 0.6)

# Projectile
projectile_dim = 0.2
projectile_loc = (0.0, 1.25, 0.6)

# Motor
motor_velocity = 4.5
release_frame = 50
simulation_end_frame = 300

# Enable physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 1. CREATE BASE (Platform)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'
base.rigid_body.mass = 100.0  # Heavy for stability

# 2. CREATE ARM (Beam)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 10.0
arm.rigid_body.use_margin = True
arm.rigid_body.collision_margin = 0.01

# 3. CREATE COUNTERWEIGHT
bpy.ops.mesh.primitive_cube_add(size=1.0, location=counterweight_loc)
counterweight = bpy.context.active_object
counterweight.name = "Counterweight"
counterweight.scale = (counterweight_dim, counterweight_dim, counterweight_dim)
bpy.ops.rigidbody.object_add()
counterweight.rigid_body.type = 'ACTIVE'
counterweight.rigid_body.collision_shape = 'BOX'
counterweight.rigid_body.mass = 50.0  # Heavy counterweight

# 4. CREATE PROJECTILE
bpy.ops.mesh.primitive_cube_add(size=1.0, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = (projectile_dim, projectile_dim, projectile_dim)
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = 1.0
projectile.rigid_body.friction = 0.5
projectile.rigid_body.restitution = 0.3

# 5. CREATE HINGE CONSTRAINT (Base to Arm)
# Select base first, then arm
bpy.context.view_layer.objects.active = base
base.select_set(True)
arm.select_set(True)
bpy.ops.rigidbody.constraint_add(type='HINGE')
hinge = bpy.context.active_object
hinge.name = "Hinge_Arm"
hinge.empty_display_type = 'SINGLE_ARROW'

# Configure hinge
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = base
hinge.rigid_body_constraint.object2 = arm
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = -1.57  # -90 degrees
hinge.rigid_body_constraint.limit_ang_z_upper = 1.57   # +90 degrees

# Position hinge at pivot point
hinge.location = (0.0, 0.0, 0.5)  # Top of base
hinge.rotation_euler = (0.0, 0.0, 0.0)

# Enable motor
hinge.rigid_body_constraint.use_motor_ang = True
hinge.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
hinge.rigid_body_constraint.motor_ang_max_impulse = 100.0

# 6. CREATE FIXED CONSTRAINT (Arm to Counterweight)
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
counterweight.select_set(True)
bpy.ops.rigidbody.constraint_add(type='FIXED')
fixed_cw = bpy.context.active_object
fixed_cw.name = "Fixed_Counterweight"
fixed_cw.rigid_body_constraint.object1 = arm
fixed_cw.rigid_body_constraint.object2 = counterweight
fixed_cw.location = counterweight_loc

# 7. CREATE FIXED CONSTRAINT (Arm to Projectile) - Temporary
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
projectile.select_set(True)
bpy.ops.rigidbody.constraint_add(type='FIXED')
fixed_proj = bpy.context.active_object
fixed_proj.name = "Fixed_Projectile"
fixed_proj.rigid_body_constraint.object1 = arm
fixed_proj.rigid_body_constraint.object2 = projectile
fixed_proj.location = projectile_loc

# 8. ANIMATE CONSTRAINT RELEASE (at frame 50)
# Set initial state: constraint enabled
fixed_proj.rigid_body_constraint.enabled = True
fixed_proj.keyframe_insert(data_path="rigid_body_constraint.enabled", frame=1)

# Set release state: constraint disabled
fixed_proj.rigid_body_constraint.enabled = False
fixed_proj.keyframe_insert(data_path="rigid_body_constraint.enabled", frame=release_frame)

# Set simulation end frame
bpy.context.scene.frame_end = simulation_end_frame

# 9. CREATE GROUND PLANE (for distance measurement)
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

print("Catapult construction complete. Projectile will release at frame", release_frame)