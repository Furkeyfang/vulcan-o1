import bpy

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
column_dim = (0.5, 0.5, 2.0)
column_loc = (0.0, 0.0, 1.25)
arm_dim = (5.0, 0.3, 0.3)
arm_loc = (2.5, 0.0, 2.4)
hook_dim = (0.2, 0.2, 0.5)
hook_loc = (5.0, 0.0, 2.0)
load_mass_kg = 400.0
gravity = 9.81
load_force_newton = 3924.0
hinge_motor_torque = 20000.0
base_softbody_stiffness = 500.0
simulation_frames = 100

# Ensure proper unit scaling (Blender uses meters)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.context.scene.gravity = (0.0, 0.0, -gravity)

# Create flexible base (soft body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.object.modifier_add(type='SOFT_BODY')
base.modifiers["Softbody"].settings.goal_default = 0.95  # Slight flexibility
base.modifiers["Softbody"].settings.goal_min = 0.8
base.modifiers["Softbody"].settings.goal_max = 1.0
base.modifiers["Softbody"].settings.goal_stiffness = base_softbody_stiffness
# Also add rigid body for constraint compatibility
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create column (rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = 100.0  # Reasonable mass for steel column

# Create arm (rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = 50.0  # Lighter than column

# Create hook (rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=hook_loc)
hook = bpy.context.active_object
hook.name = "Hook"
hook.scale = hook_dim
bpy.ops.rigidbody.object_add()
hook.rigid_body.type = 'ACTIVE'
hook.rigid_body.mass = load_mass_kg  # 400 kg load

# Constraints
# Base-Column: Fixed
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint_fixed = bpy.context.active_object
constraint_fixed.name = "Base_Column_Fixed"
constraint_fixed.location = (0.0, 0.0, 0.25)  # At interface
constraint = constraint_fixed.rigid_body_constraint
constraint.object1 = base
constraint.object2 = column

# Column-Arm: Hinge with motor
bpy.ops.rigidbody.constraint_add(type='HINGE')
constraint_hinge = bpy.context.active_object
constraint_hinge.name = "Column_Arm_Hinge"
constraint_hinge.location = (0.0, 0.0, 2.25)  # Top of column
constraint = constraint_hinge.rigid_body_constraint
constraint.object1 = column
constraint.object2 = arm
constraint.use_limit_ang_z = True
constraint.limit_ang_z_lower = -0.01  # Nearly fixed
constraint.limit_ang_z_upper = 0.01
constraint.use_motor_ang_z = True
constraint.motor_ang_z_target_velocity = 0.0
constraint.motor_ang_z_max_torque = hinge_motor_torque

# Arm-Hook: Fixed
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint_hook = bpy.context.active_object
constraint_hook.name = "Arm_Hook_Fixed"
constraint_hook.location = (5.0, 0.0, 2.25)  # At arm distal end
constraint = constraint_hook.rigid_body_constraint
constraint.object1 = arm
constraint.object2 = hook

# Apply downward force to hook via constant force constraint
bpy.ops.rigidbody.constraint_add(type='GENERIC_SPRING')
force_constraint = bpy.context.active_object
force_constraint.name = "Hook_Force"
force_constraint.location = hook_loc
constraint = force_constraint.rigid_body_constraint
constraint.object1 = hook
constraint.use_spring_x = False
constraint.use_spring_y = False
constraint.use_spring_z = True
constraint.spring_stiffness_z = 0.0  # No spring, just force
constraint.spring_damping_z = 0.0
# Force is applied via motor? Actually, generic spring can apply force along Z.
# But simpler: use a constant force via rigid body property.
hook.rigid_body.use_gravity = True  # Already includes mass*gravity
# Additional force to simulate load beyond gravity? The mass already gives 3924 N.
# So we just set the hook mass to 400 kg; gravity will apply the force.

# Set simulation frame range
bpy.context.scene.frame_end = simulation_frames

# Ensure proper collision margins
for obj in [base, column, arm, hook]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04  # Default

# Optional: Add a floor to prevent base from falling too far
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, -1.0))
floor = bpy.context.active_object
floor.name = "Floor"
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'