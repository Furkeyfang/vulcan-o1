import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
support_dim = (0.2, 0.2, 2.0)
support_loc = (0.0, 0.0, 1.5)
arm_dim = (2.0, 0.1, 0.1)
arm_loc = (1.0, 0.0, 2.5)
holder_dim = (0.1, 0.1, 0.1)
holder_loc = (2.0, 0.0, 2.5)
projectile_radius = 0.05
projectile_start = (0.0, 0.0, 2.5)
hinge_pivot = (0.0, 0.0, 2.5)
motor_velocity = 10.0

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Vertical Support Beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.name = "Support"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'

# Fixed Constraint: Base to Support
bpy.ops.rigidbody.constraint_add()
constraint_fixed = bpy.context.active_object
constraint_fixed.name = "Base_Support_Fixed"
constraint_fixed.rigid_body_constraint.type = 'FIXED'
constraint_fixed.rigid_body_constraint.object1 = base
constraint_fixed.rigid_body_constraint.object2 = support

# Create Throwing Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Throwing_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.angular_damping = 0.1

# Hinge Constraint: Support to Arm
bpy.ops.rigidbody.constraint_add()
constraint_hinge = bpy.context.active_object
constraint_hinge.name = "Arm_Hinge"
constraint_hinge.rigid_body_constraint.type = 'HINGE'
constraint_hinge.rigid_body_constraint.object1 = support
constraint_hinge.rigid_body_constraint.object2 = arm
constraint_hinge.location = hinge_pivot
constraint_hinge.rigid_body_constraint.use_limit_angle = True
constraint_hinge.rigid_body_constraint.limit_angle_min = 0.0
constraint_hinge.rigid_body_constraint.limit_angle_max = 3.14159  # 180° rotation
constraint_hinge.rigid_body_constraint.use_motor_angular = True
constraint_hinge.rigid_body_constraint.motor_angular_target_velocity = motor_velocity
constraint_hinge.rigid_body_constraint.motor_angular_max_impulse = 1000.0

# Create Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=1.0, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Projectile_Holder"
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.collision_shape = 'BOX'
holder.rigid_body.mass = 0.1

# Fixed Constraint: Arm to Holder
bpy.ops.rigidbody.constraint_add()
constraint_holder = bpy.context.active_object
constraint_holder.name = "Arm_Holder_Fixed"
constraint_holder.rigid_body_constraint.type = 'FIXED'
constraint_holder.rigid_body_constraint.object1 = arm
constraint_holder.rigid_body_constraint.object2 = holder

# Create Projectile Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=projectile_radius, location=projectile_start)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'SPHERE'
projectile.rigid_body.mass = 0.5
projectile.rigid_body.restitution = 0.8  # Bounciness

# Set collision margins (headless compatible)
for obj in [base, support, arm, holder, projectile]:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.0

# Setup World Physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create Target Visual (non-physical)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.5, depth=0.1, location=(0,0,10))
target = bpy.context.active_object
target.name = "Target"
target.display_type = 'WIRE'

print("Catapult assembly complete. Motorized hinge ready with ω =", motor_velocity, "rad/s")