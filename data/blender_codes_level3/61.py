import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== PARAMETERS (from summary) ==========
base_dim = (2.0, 2.0, 0.3)
base_center_z = 0.15

support_dim = (0.2, 0.2, 1.5)
support_x_offset = 0.8
support_bottom_z = 0.3
support_center_z = 1.05
support_top_z = 1.8

launch_arm_dim = (2.0, 0.1, 0.1)
launch_arm_center_z = 1.8

projectile_radius = 0.1
projectile_height = 0.2
projectile_center_z = 1.95

hinge_pivot_left = (-0.8, 0.0, 1.8)
hinge_pivot_right = (0.8, 0.0, 1.8)
hinge_axis = (0.0, 1.0, 0.0)  # Y-axis

motor_angular_velocity = 6.0

# ========== CREATE BASE ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, base_center_z))
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# ========== CREATE SUPPORT ARMS ==========
# Left Support
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-support_x_offset, 0.0, support_center_z))
support_left = bpy.context.active_object
support_left.name = "Support_Left"
support_left.scale = support_dim
bpy.ops.rigidbody.object_add()
support_left.rigid_body.type = 'PASSIVE'

# Right Support
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(support_x_offset, 0.0, support_center_z))
support_right = bpy.context.active_object
support_right.name = "Support_Right"
support_right.scale = support_dim
bpy.ops.rigidbody.object_add()
support_right.rigid_body.type = 'PASSIVE'

# ========== CREATE LAUNCH ARM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, launch_arm_center_z))
launch_arm = bpy.context.active_object
launch_arm.name = "Launch_Arm"
launch_arm.scale = launch_arm_dim
bpy.ops.rigidbody.object_add()
launch_arm.rigid_body.type = 'ACTIVE'
launch_arm.rigid_body.collision_shape = 'BOX'

# ========== CREATE PROJECTILE ==========
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=projectile_radius,
    depth=projectile_height,
    location=(0.0, 0.0, projectile_center_z)
)
projectile = bpy.context.active_object
projectile.name = "Projectile"
# Rotate cylinder to stand upright (default is along Z)
projectile.rotation_euler = (0.0, 0.0, 0.0)
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'CONVEX_HULL'

# ========== CREATE HINGE CONSTRAINTS ==========
# Use empty objects as hinge pivots (headless compatible method)
def create_hinge_constraint(obj_a, obj_b, pivot_location, axis):
    # Create an empty at pivot location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_location)
    pivot = bpy.context.active_object
    pivot.name = "Hinge_Pivot"
    
    # Create constraint between obj_a and obj_b using the empty as pivot
    # In headless mode, we add a generic constraint and set its properties
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = "Hinge_Constraint"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.location = pivot_location
    
    # Set pivot and axis in world coordinates
    constraint.rigid_body_constraint.pivot_type = 'CUSTOM'
    constraint.rigid_body_constraint.pivot_x = pivot_location[0]
    constraint.rigid_body_constraint.pivot_y = pivot_location[1]
    constraint.rigid_body_constraint.pivot_z = pivot_location[2]
    
    constraint.rigid_body_constraint.axis = axis
    # Set motor properties
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.use_angular_motor = True
    constraint.rigid_body_constraint.motor_angular_target_velocity = motor_angular_velocity
    constraint.rigid_body_constraint.motor_angular_max_impulse = 10.0  # Reasonable torque limit
    
    # Hide the empty (optional, but keeps scene clean)
    pivot.hide_viewport = True
    pivot.hide_render = True
    
    return constraint

# Left Hinge (Launch Arm -> Left Support)
hinge_left = create_hinge_constraint(launch_arm, support_left, hinge_pivot_left, hinge_axis)
hinge_left.name = "Hinge_Left"

# Right Hinge (Launch Arm -> Right Support)
hinge_right = create_hinge_constraint(launch_arm, support_right, hinge_pivot_right, hinge_axis)
hinge_right.name = "Hinge_Right"

# ========== SET UP PHYSICS WORLD ==========
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 200  # Verification frames

# ========== INITIAL POSITION CHECKS ==========
# Ensure launch arm is initially horizontal (rotation 0 around Y)
launch_arm.rotation_euler = (0.0, 0.0, 0.0)

print("Dual-arm launcher construction complete.")
print(f"Motor angular velocity: {motor_angular_velocity} rad/s")
print(f"Simulation will run for {bpy.context.scene.frame_end} frames.")