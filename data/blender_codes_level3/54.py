import bpy
import mathutils
from math import radians

# --- Clear Scene (headless compatible) ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Define Variables from Summary ---
# Base
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

# Crane Arm
crane_dim = (0.2, 0.2, 4.0)
crane_loc = (0.0, 0.0, 2.5)

# Catapult Arm
catapult_dim = (0.15, 0.15, 2.0)
catapult_loc = (0.0, 1.0, 4.5)

# Projectile
proj_radius = 0.2
proj_loc = (0.0, 2.0, 4.5)

# Hinge Pivots
pivot_crane = (0.0, 0.0, 0.5)
pivot_catapult = (0.0, 0.0, 4.5)

# Motor Parameters
crane_motor_velocity = 2.0
catapult_motor_velocity = 5.0
crane_rotation_target = radians(90.0)

# --- Helper to create rigid bodies ---
def add_rigidbody(obj, rb_type='ACTIVE', collision_shape='BOX'):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.collision_shape = collision_shape
    obj.rigid_body.use_margin = True
    obj.rigid_body.collision_margin = 0.0

# --- 1. Base Platform ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "Base"
add_rigidbody(base, 'PASSIVE')

# --- 2. Crane Arm ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=crane_loc)
crane = bpy.context.active_object
crane.scale = crane_dim
crane.name = "CraneArm"
add_rigidbody(crane, 'ACTIVE')

# --- 3. Catapult Arm ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=catapult_loc)
catapult = bpy.context.active_object
catapult.scale = catapult_dim
catapult.name = "CatapultArm"
add_rigidbody(catapult, 'ACTIVE')

# --- 4. Projectile Sphere ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=proj_radius, location=proj_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
add_rigidbody(projectile, 'ACTIVE', 'SPHERE')

# --- 5. Constraints (headless: create generic then set properties) ---
# Crane Hinge (Z-axis rotation at base top)
crane_constraint = base.constraints.new('RIGID_BODY_JOINT')
crane_constraint.object1 = base
crane_constraint.object2 = crane
crane_constraint.pivot_type = 'CUSTOM'
crane_constraint.pivot_x = pivot_crane[0]
crane_constraint.pivot_y = pivot_crane[1]
crane_constraint.pivot_z = pivot_crane[2]
crane_constraint.use_linear_limit = True
crane_constraint.linear_limit_x = 0.0
crane_constraint.linear_limit_y = 0.0
crane_constraint.linear_limit_z = 0.0
crane_constraint.use_angular_limit_x = True
crane_constraint.use_angular_limit_y = True
crane_constraint.angular_limit_x_min = 0.0
crane_constraint.angular_limit_x_max = 0.0
crane_constraint.angular_limit_y_min = 0.0
crane_constraint.angular_limit_y_max = 0.0
crane_constraint.use_angular_limit_z = True
crane_constraint.angular_limit_z_min = -crane_rotation_target
crane_constraint.angular_limit_z_max = 0.0  # Only clockwise (negative Z-rotation)
crane_constraint.use_motor_angular = True
crane_constraint.motor_angular_target_velocity = -crane_motor_velocity  # Negative for clockwise

# Catapult Hinge (X-axis rotation at crane top)
catapult_constraint = crane.constraints.new('RIGID_BODY_JOINT')
catapult_constraint.object1 = crane
catapult_constraint.object2 = catapult
catapult_constraint.pivot_type = 'CUSTOM'
catapult_constraint.pivot_x = pivot_catapult[0]
catapult_constraint.pivot_y = pivot_catapult[1]
catapult_constraint.pivot_z = pivot_catapult[2]
catapult_constraint.use_linear_limit = True
catapult_constraint.linear_limit_x = 0.0
catapult_constraint.linear_limit_y = 0.0
catapult_constraint.linear_limit_z = 0.0
catapult_constraint.use_angular_limit_x = True
catapult_constraint.angular_limit_x_min = -radians(90.0)  # Downward tilt range
catapult_constraint.angular_limit_x_max = 0.0
catapult_constraint.use_angular_limit_y = True
catapult_constraint.angular_limit_y_min = 0.0
catapult_constraint.angular_limit_y_max = 0.0
catapult_constraint.use_angular_limit_z = True
catapult_constraint.angular_limit_z_min = 0.0
catapult_constraint.angular_limit_z_max = 0.0
catapult_constraint.use_motor_angular = True
catapult_constraint.motor_angular_target_velocity = catapult_motor_velocity  # Positive X-rotation tilts down

# --- 6. Keyframe Motor Activation (simulate sequential actuation) ---
# Crane motor active from frame 1 to 90° rotation time
crane_constraint.motor_angular_enabled = True
crane_constraint.keyframe_insert(data_path="motor_angular_enabled", frame=1)
# Estimate frames for 90° at 2 rad/s: time = angle/velocity = 1.5708/2.0 = 0.7854s → ~19 frames at 24 fps
stop_frame = int(0.7854 * 24)  # ~19
crane_constraint.motor_angular_enabled = False
crane_constraint.keyframe_insert(data_path="motor_angular_enabled", frame=stop_frame)

# Catapult motor activates after crane stops
catapult_constraint.motor_angular_enabled = False
catapult_constraint.keyframe_insert(data_path="motor_angular_enabled", frame=1)
catapult_constraint.motor_angular_enabled = True
catapult_constraint.keyframe_insert(data_path="motor_angular_enabled", frame=stop_frame)

# --- 7. Adjust Simulation Settings for Launch ---
scene = bpy.context.scene
scene.frame_end = 150  # Enough for projectile flight
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

print("Crane-catapult hybrid constructed. Motor sequence: crane rotates 90° CW, then catapult tilts downward.")