import bpy
import math
from math import atan2

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import parameters from summary
# Tower
col_w = 1.0
col_d = 1.0
col_h = 20.0
col_center_z = col_h / 2.0

# Bracing
br_w = 0.2
br_d = 0.2
br_nom_len = 3.0
br_bot_z = 1.0
br_top_z = 19.0
br_count = 4

# Geometry
col_half_w = col_w / 2.0
col_half_d = col_d / 2.0

# Wind load
wind_mass = 600.0
g = 9.81
wind_force = wind_mass * g
wind_loc_z = col_h
wind_dir = (1.0, 0.0, 0.0)

# Calculated
diag_len = (col_w**2 + (br_top_z - br_bot_z)**2)**0.5
br_scale_z = diag_len / br_nom_len
br_mid_z = (br_bot_z + br_top_z) / 2.0
br_angle = atan2(col_w, (br_top_z - br_bot_z))  # Same for both planes

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 1. Create Main Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, col_center_z))
column = bpy.context.active_object
column.name = "MainColumn"
column.scale = (col_w, col_d, col_h)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = col_w * col_d * col_h * 7850  # Steel density

# 2. Create Bracing Elements
brace_definitions = [
    # (name, plane, x_sign, y_sign, rotation_axis)
    ("Brace_XZ_0", "XZ", 1, 0, (0, 1, 0)),    # 0°: +X to -X
    ("Brace_XZ_180", "XZ", -1, 0, (0, 1, 0)), # 180°: -X to +X
    ("Brace_YZ_90", "YZ", 0, 1, (1, 0, 0)),   # 90°: +Y to -Y
    ("Brace_YZ_270", "YZ", 0, -1, (1, 0, 0))  # 270°: -Y to +Y
]

braces = []
for name, plane, x_sign, y_sign, rot_axis in brace_definitions:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, br_mid_z))
    brace = bpy.context.active_object
    brace.name = name
    
    # Scale to cross-section and length
    brace.scale = (br_w, br_d, br_scale_z)
    
    # Position midpoint based on plane
    if plane == "XZ":
        brace.location.x = x_sign * col_half_w
        brace.location.y = 0
    else:  # YZ
        brace.location.x = 0
        brace.location.y = y_sign * col_half_d
    
    # Rotate to diagonal orientation
    # Original cube local Z is along length, need to rotate to match diagonal
    if plane == "XZ":
        # Rotate around Y-axis
        brace.rotation_euler = (0, br_angle * x_sign, 0)
    else:  # YZ
        # Rotate around X-axis
        brace.rotation_euler = (br_angle * y_sign, 0, 0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    brace.rigid_body.type = 'ACTIVE'
    brace.rigid_body.mass = br_w * br_d * diag_len * 7850
    
    braces.append(brace)

# 3. Create Ground (passive rigid body for constraint)
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# 4. Create Fixed Constraints
# Column to Ground (foundation)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "ColumnBaseConstraint"

bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = ground
constraint.object2 = column

# Braces to Column (welded connections)
for i, brace in enumerate(braces):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=brace.location)
    brace_constraint = bpy.context.active_object
    brace_constraint.name = f"BraceConstraint_{i}"
    
    bpy.ops.rigidbody.constraint_add()
    bc = brace_constraint.rigid_body_constraint
    bc.type = 'FIXED'
    bc.object1 = column
    bc.object2 = brace

# 5. Apply Wind Force (Force Field at top)
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, wind_loc_z))
wind_field = bpy.context.active_object
wind_field.name = "WindForce"
wind_field.field.type = 'FORCE'
wind_field.field.strength = wind_force
wind_field.field.direction_x, wind_field.field.direction_y, wind_field.field.direction_z = wind_dir
wind_field.field.use_max_distance = True
wind_field.field.distance_max = 5.0  # Affects top region only

# Limit force field to affect only tower components
wind_field.field.affect_gravity = False

# 6. Set up simulation
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.enabled = True

print("Tower construction complete. Run simulation with: bpy.ops.ptcache.bake_all()")