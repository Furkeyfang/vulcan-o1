import bpy
import math
from mathutils import Matrix, Vector, Euler

# === 1. CLEAR SCENE ===
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# === 2. PARAMETERS (from summary) ===
# Base
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

# Arm
arm_dim = (0.2, 2.0, 0.2)
arm_hinge_loc = (0.0, 0.0, 0.5)
arm_initial_rot_deg = -30.0
arm_pivot_offset = (0.0, 1.0, 0.0)

# Spring
spring_radius = 0.1
spring_height = 0.5
spring_base_attach = (0.0, 0.5, 0.25)
spring_arm_attach_local = (0.0, 0.5, 0.5)
spring_rest_length = 0.7
spring_stiffness = 5000.0
spring_damping = 50.0

# Lock
lock_dim = (0.1, 0.1, 0.1)
lock_loc = (0.1, 1.5, 0.5)
lock_initial_rot_deg = -45.0
lock_hinge_axis = 'Y'

# Projectile
proj_radius = 0.2
proj_mass = 1.0
proj_initial_y = 1.732
proj_initial_z = 1.5

# Simulation
frame_release = 50
frame_end = 250
gravity_z = -9.81

# === 3. PHYSICS WORLD SETUP ===
bpy.context.scene.gravity = (0, 0, gravity_z)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.enable_deactivation = False

# === 4. BASE PLATFORM ===
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'
base.rigid_body.mass = 100.0  # Heavy and static

# === 5. LAUNCH ARM ===
# Create arm at hinge location, then offset to center
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_hinge_loc)
arm = bpy.context.active_object
arm.name = "Launch_Arm"
arm.scale = arm_dim
# Move pivot to hinge end (one end of arm)
arm.data.transform(Matrix.Translation((-arm_pivot_offset[0], -arm_pivot_offset[1], -arm_pivot_offset[2])))
arm.location = arm_hinge_loc
# Apply initial rotation
arm.rotation_euler = Euler((math.radians(arm_initial_rot_deg), 0, 0), 'XYZ')
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 5.0
arm.rigid_body.linear_damping = 0.04
arm.rigid_body.angular_damping = 0.1

# === 6. ARM HINGE CONSTRAINT ===
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm_hinge_loc)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Arm_Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge_empty.rigid_body_constraint.type = 'HINGE'
hinge_empty.rigid_body_constraint.object1 = base
hinge_empty.rigid_body_constraint.object2 = arm
hinge_empty.rigid_body_constraint.use_limit_lin_z = True
hinge_empty.rigid_body_constraint.limit_lin_z_lower = 0
hinge_empty.rigid_body_constraint.limit_lin_z_upper = 0
hinge_empty.rigid_body_constraint.use_limit_ang_x = True
hinge_empty.rigid_body_constraint.limit_ang_x_lower = math.radians(-90)
hinge_empty.rigid_body_constraint.limit_ang_x_upper = math.radians(90)

# === 7. SPRING VISUAL (cylinder) ===
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=spring_radius,
    depth=spring_height,
    location=spring_base_attach
)
spring_vis = bpy.context.active_object
spring_vis.name = "Spring_Visual"
spring_vis.rotation_euler = Euler((0, math.radians(90), 0), 'XYZ')
bpy.ops.rigidbody.object_add()
spring_vis.rigid_body.type = 'PASSIVE'
spring_vis.rigid_body.collision_shape = 'CYLINDER'
spring_vis.rigid_body.mass = 0.1

# === 8. SPRING CONSTRAINT ===
# Create two empties for spring attachment points
bpy.ops.object.empty_add(type='SPHERE', location=spring_base_attach)
spring_anchor = bpy.context.active_object
spring_anchor.name = "Spring_Anchor"
spring_anchor.empty_display_size = 0.05

# Calculate arm attachment point in world coordinates
arm_matrix = arm.matrix_world
arm_attach_world = arm_matrix @ Vector(spring_arm_attach_local)
bpy.ops.object.empty_add(type='SPHERE', location=arm_attach_world)
spring_arm_point = bpy.context.active_object
spring_arm_point.name = "Spring_Arm_Point"
spring_arm_point.empty_display_size = 0.05

# Fix empties to their respective objects
for empty, parent in [(spring_anchor, base), (spring_arm_point, arm)]:
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = parent
    empty.rigid_body_constraint.object2 = empty

# Spring constraint between empties
bpy.ops.object.empty_add(type='PLAIN_AXES', location=spring_base_attach)
spring_constraint = bpy.context.active_object
spring_constraint.name = "Spring_Constraint"
bpy.ops.rigidbody.constraint_add()
spring_constraint.rigid_body_constraint.type = 'SPRING'
spring_constraint.rigid_body_constraint.object1 = spring_anchor
spring_constraint.rigid_body_constraint.object2 = spring_arm_point
spring_constraint.rigid_body_constraint.spring_length = spring_rest_length
spring_constraint.rigid_body_constraint.spring_stiffness = spring_stiffness
spring_constraint.rigid_body_constraint.spring_damping = spring_damping
spring_constraint.rigid_body_constraint.use_spring = True

# === 9. RELEASE LOCK ===
bpy.ops.mesh.primitive_cube_add(size=1, location=lock_loc)
lock = bpy.context.active_object
lock.name = "Release_Lock"
lock.scale = lock_dim
lock.rotation_euler = Euler((0, math.radians(lock_initial_rot_deg), 0), 'XYZ')
bpy.ops.rigidbody.object_add()
lock.rigid_body.type = 'ACTIVE'
lock.rigid_body.collision_shape = 'BOX'
lock.rigid_body.mass = 0.5
lock.rigid_body.linear_damping = 0.1
lock.rigid_body.angular_damping = 0.2

# Lock hinge constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=lock_loc)
lock_hinge = bpy.context.active_object
lock_hinge.name = "Lock_Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
lock_hinge.rigid_body_constraint.type = 'HINGE'
lock_hinge.rigid_body_constraint.object1 = base
lock_hinge.rigid_body_constraint.object2 = lock
lock_hinge.rigid_body_constraint.use_limit_lin_z = True
lock_hinge.rigid_body_constraint.limit_lin_z_lower = 0
lock_hinge.rigid_body_constraint.limit_lin_z_upper = 0
# Motor setup for initial hold
lock_hinge.rigid_body_constraint.use_motor_ang = True
lock_hinge.rigid_body_constraint.motor_ang_target_velocity = 0.0
lock_hinge.rigid_body_constraint.motor_ang_max_impulse = 100.0

# === 10. PROJECTILE ===
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=proj_radius,
    location=(0, proj_initial_y, proj_initial_z)
)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'SPHERE'
projectile.rigid_body.mass = proj_mass
projectile.rigid_body.linear_damping = 0.01
projectile.rigid_body.angular_damping = 0.05
projectile.rigid_body.use_continuous_collision = True
projectile.rigid_body.ccd_motion_threshold = 0.001

# === 11. ANIMATE LOCK RELEASE ===
# Set keyframes for motor enable/disable
lock_hinge.rigid_body_constraint.use_motor_ang = True
lock_hinge.rigid_body_constraint.keyframe_insert(data_path="use_motor_ang", frame=1)
lock_hinge.rigid_body_constraint.use_motor_ang = False
lock_hinge.rigid_body_constraint.keyframe_insert(data_path="use_motor_ang", frame=frame_release)

# === 12. SCENE SETTINGS ===
bpy.context.scene.frame_end = frame_end
bpy.context.scene.render.fps = 24

print("Catapult assembly complete. Simulation will release lock at frame", frame_release)
print("Projectile target: Y > 8m within", frame_end, "frames")