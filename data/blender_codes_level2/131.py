import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
col_dim = (0.3, 0.3, 2.0)
col_loc = (0.0, 0.0, 1.0)
arm_dim = (0.2, 0.2, 3.0)
arm_loc = (1.5, 0.0, 2.1)
load_rad = 0.1
load_depth = 0.3
load_loc = (3.15, 0.0, 2.1)
load_mass = 500.0
con_strength = 10000.0

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)

# 1. Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.name = "Support_Column"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# 2. Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = 10.0  # Estimated mass based on volume (0.2*0.2*3=0.12 m³) * density

# 3. Create Load Cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=load_rad,
    depth=load_depth,
    location=load_loc
)
load = bpy.context.active_object
load.name = "Load"
load.rotation_euler = (0, 0.5 * 3.14159, 0)  # Rotate 90° around Y to align with X-axis
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# 4. Add Fixed Constraint: Column ↔ Arm
# Create empty for constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 2.0))
con1 = bpy.context.active_object
con1.name = "Constraint_Column_Arm"
bpy.ops.rigidbody.constraint_add()
con1.rigid_body_constraint.type = 'FIXED'
con1.rigid_body_constraint.object1 = column
con1.rigid_body_constraint.object2 = arm
con1.rigid_body_constraint.use_breaking = True
con1.rigid_body_constraint.breaking_threshold = con_strength

# 5. Add Fixed Constraint: Arm ↔ Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(3.0, 0, 2.1))
con2 = bpy.context.active_object
con2.name = "Constraint_Arm_Load"
bpy.ops.rigidbody.constraint_add()
con2.rigid_body_constraint.type = 'FIXED'
con2.rigid_body_constraint.object1 = arm
con2.rigid_body_constraint.object2 = load
con2.rigid_body_constraint.use_breaking = True
con2.rigid_body_constraint.breaking_threshold = con_strength

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Keyframe initial state
bpy.context.scene.frame_set(1)
for obj in [column, arm, load]:
    obj.keyframe_insert(data_path="location")
    obj.keyframe_insert(data_path="rotation_euler")

# Run simulation for 2 seconds (120 frames at 60 fps)
bpy.context.scene.frame_end = 120

# Optional: Bake simulation for headless verification
bpy.ops.ptcache.bake_all(bake=True)