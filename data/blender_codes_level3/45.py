import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
support_dim = (0.2, 0.2, 2.0)
support_loc = (0.0, 0.0, 1.25)
arm_dim = (0.15, 0.15, 2.5)
arm_pivot_loc = (0.0, 0.0, 2.25)
arm_initial_angle = -30.0
holder_dim = (0.3, 0.3, 0.3)
holder_offset = 1.25
projectile_radius = 0.15
motor_velocity = 5.0
constraint_break_threshold = 50.0
target_center = (10.0, 0.0, 0.0)
target_dim = (2.0, 2.0, 0.1)
simulation_frames = 100

# Convert angle to radians
angle_rad = math.radians(arm_initial_angle)

# Calculate projectile holder initial position
holder_x = holder_offset * math.cos(angle_rad)
holder_z = arm_pivot_loc[2] + holder_offset * math.sin(angle_rad)
holder_loc = (holder_x, 0.0, holder_z)

# Enable rigid body physics
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.frame_end = simulation_frames

# ==================== BASE PLATFORM ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# ==================== SUPPORT ARM ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.name = "Support_Arm"
support.scale = support_dim
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'

# Fixed constraint: Base → Support Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=support_loc)
constraint_fixed = bpy.context.active_object
constraint_fixed.name = "Constraint_Base_Support"
constraint_fixed.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
constraint_fixed.rigid_body_constraint.type = 'FIXED'
constraint_fixed.rigid_body_constraint.object1 = base
constraint_fixed.rigid_body_constraint.object2 = support

# ==================== THROWING ARM ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_pivot_loc)
arm = bpy.context.active_object
arm.name = "Throwing_Arm"
arm.scale = arm_dim
arm.rotation_euler = (0.0, angle_rad, 0.0)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.angular_damping = 0.1  # Reduce wobble

# ==================== PROJECTILE HOLDER ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Projectile_Holder"
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.collision_shape = 'BOX'

# ==================== PROJECTILE ====================
bpy.ops.mesh.primitive_uv_sphere_add(radius=projectile_radius, location=holder_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = 0.5  # 0.5kg projectile
projectile.rigid_body.collision_shape = 'SPHERE'

# ==================== CONSTRAINTS ====================
# Hinge constraint: Support Arm → Throwing Arm (Motorized)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm_pivot_loc)
constraint_hinge = bpy.context.active_object
constraint_hinge.name = "Constraint_Hinge_Motor"
constraint_hinge.empty_display_size = 0.4
bpy.ops.rigidbody.constraint_add()
constraint_hinge.rigid_body_constraint.type = 'HINGE'
constraint_hinge.rigid_body_constraint.use_motor = True
constraint_hinge.rigid_body_constraint.motor_target_velocity = motor_velocity
constraint_hinge.rigid_body_constraint.object1 = support
constraint_hinge.rigid_body_constraint.object2 = arm
constraint_hinge.rigid_body_constraint.use_limit_angle = False

# Fixed constraint: Throwing Arm → Projectile Holder (Breakable)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=holder_loc)
constraint_holder = bpy.context.active_object
constraint_holder.name = "Constraint_Arm_Holder"
constraint_holder.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
constraint_holder.rigid_body_constraint.type = 'FIXED'
constraint_holder.rigid_body_constraint.object1 = arm
constraint_holder.rigid_body_constraint.object2 = holder
constraint_holder.rigid_body_constraint.use_breaking = True
constraint_holder.rigid_body_constraint.breaking_threshold = constraint_break_threshold

# Fixed constraint: Projectile Holder → Projectile (Breakable)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=holder_loc)
constraint_projectile = bpy.context.active_object
constraint_projectile.name = "Constraint_Holder_Projectile"
constraint_projectile.empty_display_size = 0.2
bpy.ops.rigidbody.constraint_add()
constraint_projectile.rigid_body_constraint.type = 'FIXED'
constraint_projectile.rigid_body_constraint.object1 = holder
constraint_projectile.rigid_body_constraint.object2 = projectile
constraint_projectile.rigid_body_constraint.use_breaking = True
constraint_projectile.rigid_body_constraint.breaking_threshold = constraint_break_threshold * 0.5  # Easier to break

# ==================== TARGET ZONE ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=target_center)
target = bpy.context.active_object
target.name = "Target_Zone"
target.scale = target_dim
target.color = (1.0, 0.2, 0.2, 0.3)  # Red transparent
bpy.ops.rigidbody.object_add()
target.rigid_body.type = 'PASSIVE'
target.rigid_body.collision_shape = 'BOX'

# Set up material for target (visualization only)
mat = bpy.data.materials.new(name="Target_Material")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.2, 0.2, 0.3)
mat.blend_method = 'BLEND'
target.data.materials.append(mat)

# ==================== FINAL SETUP ====================
# Parent holder and constraints to arm for cleaner hierarchy
holder.parent = arm
constraint_holder.parent = arm
constraint_projectile.parent = holder

# Set initial linear velocity to zero for all active bodies
for obj in [arm, holder, projectile]:
    if obj.rigid_body and obj.rigid_body.type == 'ACTIVE':
        obj.rigid_body.linear_damping = 0.1
        obj.rigid_body.angular_damping = 0.2

print("Catapult construction complete. Motor velocity:", motor_velocity, "rad/s")
print("Projectile initial position:", holder_loc)
print("Target zone at:", target_center)