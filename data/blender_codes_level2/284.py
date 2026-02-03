import bpy
import math
from mathutils import Matrix

# === 1. Clear Scene ===
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# === 2. Define Variables ===
col_h = 14.0
col_cs = 1.0
col_center = (0.0, 0.0, 7.0)

arm_cs = 0.5
arm_len = 5.0
arm_right_end = (3.0, 0.0, 18.0)
arm_left_end = (-3.0, 0.0, 18.0)
arm_right_center = (1.5, 0.0, 16.0)
arm_left_center = (-1.5, 0.0, 16.0)
arm_right_angle = math.atan2(3.0, 4.0)  # 36.87° in radians
arm_left_angle = -arm_right_angle

load_mass = 400.0
load_size = 0.5
load_right_center = (3.0, 0.0, 18.0)
load_left_center = (-3.0, 0.0, 18.0)

# === 3. Create Central Column ===
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_center)
column = bpy.context.active_object
column.scale = (col_cs, col_cs, col_h)  # Z scaled to height
column.name = "Central_Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# === 4. Create Right Arm ===
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_right_center)
arm_right = bpy.context.active_object
arm_right.name = "Arm_Right"
# Scale: cross-section in XY, length in Z
arm_right.scale = (arm_cs, arm_cs, arm_len/2.0)  # Default cube length=2
# Rotate about Y-axis to align with vector (3,0,4)
arm_right.rotation_euler = (0.0, arm_right_angle, 0.0)
bpy.ops.rigidbody.object_add()
arm_right.rigid_body.type = 'PASSIVE'

# === 5. Create Left Arm ===
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_left_center)
arm_left = bpy.context.active_object
arm_left.name = "Arm_Left"
arm_left.scale = (arm_cs, arm_cs, arm_len/2.0)
arm_left.rotation_euler = (0.0, arm_left_angle, 0.0)
bpy.ops.rigidbody.object_add()
arm_left.rigid_body.type = 'PASSIVE'

# === 6. Create Load Cubes ===
# Right load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_right_center)
load_right = bpy.context.active_object
load_right.name = "Load_Right"
load_right.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load_right.rigid_body.mass = load_mass
load_right.rigid_body.type = 'ACTIVE'

# Left load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_left_center)
load_left = bpy.context.active_object
load_left.name = "Load_Left"
load_left.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load_left.rigid_body.mass = load_mass
load_left.rigid_body.type = 'ACTIVE'

# === 7. Create Fixed Constraints ===
# Constraint between column and right arm (at column top)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 14.0))
con1 = bpy.context.active_object
con1.name = "Con_Col_to_ArmR"
bpy.ops.rigidbody.constraint_add()
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = column
con1.rigid_body_constraint.object2 = arm_right

# Constraint between column and left arm (same location)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 14.0))
con2 = bpy.context.active_object
con2.name = "Con_Col_to_ArmL"
bpy.ops.rigidbody.constraint_add()
con2.rigid_body_constraint.type = 'FIXED'
con2.rigid_body_constraint.object1 = column
con2.rigid_body_constraint.object2 = arm_left

# Constraint between right arm and its load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm_right_end)
con3 = bpy.context.active_object
con3.name = "Con_ArmR_to_Load"
bpy.ops.rigidbody.constraint_add()
con3.rigid_body_constraint.type = 'FIXED'
con3.rigid_body_constraint.object1 = arm_right
con3.rigid_body_constraint.object2 = load_right

# Constraint between left arm and its load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm_left_end)
con4 = bpy.context.active_object
con4.name = "Con_ArmL_to_Load"
bpy.ops.rigidbody.constraint_add()
con4.rigid_body_constraint.type = 'FIXED'
con4.rigid_body_constraint.object1 = arm_left
con4.rigid_body_constraint.object2 = load_left

# === 8. Set World Gravity (Standard) ===
if bpy.context.scene.rigidbody_world:
    bpy.context.scene.rigidbody_world.gravity[2] = -9.81

print("Y-shaped tower construction complete.")