import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from parameter summary
base_dim = (0.5, 0.5, 3.0)
base_loc = (0.0, 0.0, 0.0)

arm1_dim = (4.0, 0.3, 0.3)
arm1_pivot = (0.0, 0.0, 3.0)
arm1_center = (2.0, 0.0, 3.0)

arm2_dim = (3.0, 0.3, 0.3)
arm2_pivot = (4.0, 0.0, 3.0)
arm2_center = (5.5, 0.0, 3.0)

effector_dim = (0.2, 0.2, 0.2)
effector_loc = (7.0, 0.0, 3.0)

joint_axis = (0.0, 0.0, 1.0)
motor_velocity = 2.0

# 1. Create Base (vertical column)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'  # Static base

# 2. Create First Arm Segment
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm1_center)
arm1 = bpy.context.active_object
arm1.name = "Arm1"
arm1.scale = arm1_dim
bpy.ops.rigidbody.object_add()
arm1.rigid_body.type = 'ACTIVE'

# 3. Create Second Arm Segment
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm2_center)
arm2 = bpy.context.active_object
arm2.name = "Arm2"
arm2.scale = arm2_dim
bpy.ops.rigidbody.object_add()
arm2.rigid_body.type = 'ACTIVE'

# 4. Create End Effector
bpy.ops.mesh.primitive_cube_add(size=1.0, location=effector_loc)
effector = bpy.context.active_object
effector.name = "EndEffector"
effector.scale = effector_dim
bpy.ops.rigidbody.object_add()
effector.rigid_body.type = 'ACTIVE'

# 5. Create Constraints
# First Hinge: Base to Arm1
bpy.ops.rigidbody.constraint_add()
constraint1 = bpy.context.active_object
constraint1.name = "Joint1_Hinge"
constraint1.empty_display_type = 'SINGLE_ARROW'
constraint1.empty_display_size = 0.5
constraint1.location = arm1_pivot

constraint1.rigid_body_constraint.type = 'HINGE'
constraint1.rigid_body_constraint.object1 = base
constraint1.rigid_body_constraint.object2 = arm1
constraint1.rigid_body_constraint.use_limit_ang_z = True
constraint1.rigid_body_constraint.limit_ang_z_lower = -3.14159  # -180°
constraint1.rigid_body_constraint.limit_ang_z_upper = 3.14159   # +180°
constraint1.rigid_body_constraint.use_motor_ang = True
constraint1.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
constraint1.rigid_body_constraint.motor_ang_max_torque = 1000.0  # High torque for reliable motion

# Second Hinge: Arm1 to Arm2
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.name = "Joint2_Hinge"
constraint2.empty_display_type = 'SINGLE_ARROW'
constraint2.empty_display_size = 0.5
constraint2.location = arm2_pivot

constraint2.rigid_body_constraint.type = 'HINGE'
constraint2.rigid_body_constraint.object1 = arm1
constraint2.rigid_body_constraint.object2 = arm2
constraint2.rigid_body_constraint.use_limit_ang_z = True
constraint2.rigid_body_constraint.limit_ang_z_lower = -3.14159
constraint2.rigid_body_constraint.limit_ang_z_upper = 3.14159
constraint2.rigid_body_constraint.use_motor_ang = True
constraint2.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
constraint2.rigid_body_constraint.motor_ang_max_torque = 1000.0

# Fixed Constraint: Arm2 to End Effector
bpy.ops.rigidbody.constraint_add()
constraint3 = bpy.context.active_object
constraint3.name = "EndEffector_Fixed"
constraint3.empty_display_type = 'CUBE'
constraint3.empty_display_size = 0.2
constraint3.location = effector_loc

constraint3.rigid_body_constraint.type = 'FIXED'
constraint3.rigid_body_constraint.object1 = arm2
constraint3.rigid_body_constraint.object2 = effector

# 6. Set initial rotation for visual clarity (optional)
# Arms are already aligned with +X due to their placement

print("Dual-joint crane constructed successfully.")
print(f"Base: {base.name} at {base.location}")
print(f"Arm1: {arm1.name} at {arm1.location}")
print(f"Arm2: {arm2.name} at {arm2.location}")
print(f"EndEffector: {effector.name} at {effector.location}")
print(f"Hinge motors set to {motor_velocity} rad/s")