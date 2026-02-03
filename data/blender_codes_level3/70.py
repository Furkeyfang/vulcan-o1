import bpy
import math
from math import cos, sin

# ========== PARAMETERS FROM SUMMARY ==========
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

tube_radius = 0.3
tube_depth = 2.0
tube_tilt_deg = 15.0
tube_tilt_rad = math.radians(tube_tilt_deg)
tube_loc = (cos(tube_tilt_rad), 0.0, 0.25 - sin(tube_tilt_rad))

projectile_radius = 0.25
projectile_depth = 0.5
projectile_loc = (0.25 * cos(tube_tilt_rad), 0.0, 0.25 + 0.25 * sin(tube_tilt_rad))

hinge_pivot = (0.0, 0.0, 0.25)
motor_velocity = 20.0
motor_duration_frames = 10
frame_rate = 24.0

# ========== SCENE SETUP ==========
# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Set scene frame rate
bpy.context.scene.render.fps = int(frame_rate)

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# ========== BASE PLATFORM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# ========== LAUNCH TUBE ==========
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=tube_radius,
    depth=tube_depth,
    location=tube_loc
)
tube = bpy.context.active_object
tube.name = "LaunchTube"
# Rotate: first align cylinder along X (rotate 90° around Y), then tilt 15° around Y
tube.rotation_euler = (0.0, tube_tilt_rad + math.radians(90.0), 0.0)
bpy.ops.rigidbody.object_add()
tube.rigid_body.type = 'PASSIVE'
tube.rigid_body.collision_shape = 'CYLINDER'

# ========== PROJECTILE ==========
bpy.ops.mesh.primitive_cylinder_add(
    vertices=24,
    radius=projectile_radius,
    depth=projectile_depth,
    location=projectile_loc
)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.rotation_euler = (0.0, tube_tilt_rad + math.radians(90.0), 0.0)
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'CYLINDER'
projectile.rigid_body.use_margin = True
projectile.rigid_body.collision_margin = 0.001

# ========== CONSTRAINTS ==========
# Fixed constraint between Base and LaunchTube
bpy.ops.rigidbody.constraint_add()
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Base_Tube"
fixed_constraint.rigid_body_constraint.type = 'FIXED'
fixed_constraint.rigid_body_constraint.object1 = base
fixed_constraint.rigid_body_constraint.object2 = tube

# Hinge constraint between LaunchTube and Projectile
bpy.ops.rigidbody.constraint_add()
hinge_constraint = bpy.context.active_object
hinge_constraint.name = "Hinge_Tube_Projectile"
hinge_constraint.location = hinge_pivot
hinge_constraint.rigid_body_constraint.type = 'HINGE'
hinge_constraint.rigid_body_constraint.object1 = tube
hinge_constraint.rigid_body_constraint.object2 = projectile
# Hinge axis: Global X (for rotation around Y)
hinge_constraint.rigid_body_constraint.axis = 'LOCAL_X'  # LOCAL_X of constraint object (which is aligned with world if rotation is zero)
hinge_constraint.rotation_euler = (0.0, 0.0, 0.0)  # Ensure constraint axes align with world

# Motor settings
hinge_constraint.rigid_body_constraint.use_motor = True
hinge_constraint.rigid_body_constraint.motor_velocity = motor_velocity
# Keyframe motor activation: ON for frames 1-10, OFF afterwards
hinge_constraint.rigid_body_constraint.use_motor = True
hinge_constraint.keyframe_insert(data_path="rigid_body_constraint.use_motor", frame=1)
hinge_constraint.rigid_body_constraint.use_motor = False
hinge_constraint.keyframe_insert(data_path="rigid_body_constraint.use_motor", frame=motor_duration_frames + 1)

# Set simulation duration
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250  # Enough to observe trajectory