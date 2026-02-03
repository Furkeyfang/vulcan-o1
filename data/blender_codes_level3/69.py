import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
support_dim = (0.2, 0.2, 2.5)
support_loc = (0.0, 0.0, 1.75)
throw_dim = (1.5, 0.15, 0.15)
throw_loc = (0.75, 0.0, 3.0)
holder_dim = (0.3, 0.3, 0.3)
holder_loc = (1.5, 0.0, 3.0)
proj_radius = 0.1
proj_loc = (1.5, 0.0, 3.0)
hinge_axis = (0.0, 1.0, 0.0)
motor_velocity = 6.0
hinge_limit_lower = 0.0
hinge_limit_upper = 2.356  # 135 degrees
sim_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Helper function to create rigid body
def add_rigid_body(obj, body_type='ACTIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.linear_damping = 0.04
    obj.rigid_body.angular_damping = 0.1

# 1. Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
add_rigid_body(base, 'PASSIVE', 100.0)  # Heavy and static

# 2. Support Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=support_loc)
support = bpy.context.active_object
support.name = "Support"
support.scale = support_dim
add_rigid_body(support, 'PASSIVE', 50.0)

# 3. Throwing Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=throw_loc)
throw = bpy.context.active_object
throw.name = "ThrowArm"
throw.scale = throw_dim
add_rigid_body(throw, 'ACTIVE', 5.0)

# 4. Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=1, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Holder"
holder.scale = holder_dim
add_rigid_body(holder, 'ACTIVE', 2.0)

# 5. Projectile (Sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=proj_radius, location=proj_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
add_rigid_body(projectile, 'ACTIVE', 1.0)

# Constraints
# Fixed: Base to Support
bpy.ops.rigidbody.constraint_add()
con1 = bpy.context.active_object
con1.name = "Base_Support_Fixed"
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = base
con1.rigid_body_constraint.object2 = support
con1.location = (0, 0, 0.5)  # At top center of base

# Hinge: Support to Throwing Arm
bpy.ops.rigidbody.constraint_add()
con2 = bpy.context.active_object
con2.name = "Support_Throw_Hinge"
con2.rigid_body_constraint.type = 'HINGE'
con2.rigid_body_constraint.object1 = support
con2.rigid_body_constraint.object2 = throw
con2.location = (0, 0, 3.0)  # At top of support
con2.rigid_body_constraint.use_limit_angular = True
con2.rigid_body_constraint.limit_angular_lower = hinge_limit_lower
con2.rigid_body_constraint.limit_angular_upper = hinge_limit_upper
con2.rigid_body_constraint.use_motor_angular = True
con2.rigid_body_constraint.motor_angular_target_velocity = motor_velocity
con2.rigid_body_constraint.motor_angular_max_impulse = 100.0
# Set hinge axis to Y (global)
con2.rigid_body_constraint.axis_primary = 'Y'
# Align constraint rotation to global Y
con2.rotation_euler = (0, 0, 0)

# Fixed: Throwing Arm to Holder
bpy.ops.rigidbody.constraint_add()
con3 = bpy.context.active_object
con3.name = "Throw_Holder_Fixed"
con3.rigid_body_constraint.type = 'FIXED'
con3.rigid_body_constraint.object1 = throw
con3.rigid_body_constraint.object2 = holder
con3.location = holder_loc

# Simulation setup
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.point_cache.frame_end = sim_frames

# Optional: Bake simulation to ensure consistency in headless mode
bpy.ops.ptcache.bake_all(bake=True)

print("Catapult assembly complete. Simulation ready.")