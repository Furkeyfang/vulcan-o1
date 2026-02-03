import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 0.1, 0.1)
base_loc = (0.0, 0.0, 0.0)
diag_dim = (0.1, 0.1, 5.2)
diag_angle = math.radians(16.7)  # Convert to radians
left_diag_mid = (-0.75, 0.0, 2.5)
right_diag_mid = (0.75, 0.0, 2.5)
rung_heights = [1.25, 2.5, 3.75]
rung_dim = (0.8, 0.05, 0.02)
apex_platform_dim = (0.2, 0.2, 0.2)
apex_platform_loc = (0.0, 0.0, 5.0)
load_mass = 300.0
load_radius = 0.2
load_loc = (0.0, 0.0, 5.4)

# Create Base Member
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.name = "Base"

# Create Left Diagonal
bpy.ops.mesh.primitive_cube_add(size=1, location=left_diag_mid)
left_diag = bpy.context.active_object
left_diag.scale = diag_dim
left_diag.rotation_euler = (0, diag_angle, 0)  # Rotate around Y
bpy.ops.rigidbody.object_add()
left_diag.rigid_body.type = 'PASSIVE'
left_diag.name = "Left_Diagonal"

# Create Right Diagonal
bpy.ops.mesh.primitive_cube_add(size=1, location=right_diag_mid)
right_diag = bpy.context.active_object
right_diag.scale = diag_dim
right_diag.rotation_euler = (0, -diag_angle, 0)
bpy.ops.rigidbody.object_add()
right_diag.rigid_body.type = 'PASSIVE'
right_diag.name = "Right_Diagonal"

# Create Rungs
rung_objects = []
for i, z in enumerate(rung_heights):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
    rung = bpy.context.active_object
    rung.scale = rung_dim
    bpy.ops.rigidbody.object_add()
    rung.rigid_body.type = 'PASSIVE'
    rung.name = f"Rung_{i+1}"
    rung_objects.append(rung)

# Create Apex Platform (load distribution)
bpy.ops.mesh.primitive_cube_add(size=1, location=apex_platform_loc)
apex_plat = bpy.context.active_object
apex_plat.scale = apex_platform_dim
bpy.ops.rigidbody.object_add()
apex_plat.rigid_body.type = 'PASSIVE'
apex_plat.name = "Apex_Platform"

# Create Load Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=load_radius, location=load_loc)
load = bpy.context.active_object
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.type = 'ACTIVE'
load.name = "Load_Sphere"

# Create Fixed Constraints
def add_fixed_constraint(obj1, obj2, location):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint = bpy.context.active_object
    constraint.empty_display_size = 0.1
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

# Base-Diagonal joints
add_fixed_constraint(base, left_diag, (-1.5, 0, 0))
add_fixed_constraint(base, right_diag, (1.5, 0, 0))

# Diagonal-Rung joints
for rung, z in zip(rung_objects, rung_heights):
    x_left = -1.5 * (1 - z/5)  # X on left diagonal at height z
    x_right = 1.5 * (1 - z/5)   # X on right diagonal at height z
    # Left attachment (rung's local -X end at x_left)
    add_fixed_constraint(left_diag, rung, (x_left, 0, z))
    # Right attachment (rung's local +X end at x_right)
    add_fixed_constraint(right_diag, rung, (x_right, 0, z))

# Diagonal-Apex joints (connect apex platform to both diagonals)
add_fixed_constraint(left_diag, apex_plat, (0, 0, 5))
add_fixed_constraint(right_diag, apex_plat, (0, 0, 5))

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100