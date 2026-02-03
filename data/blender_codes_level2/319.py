import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
base_dim = (6.0, 4.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
level1_dim = (4.0, 3.0, 0.3)
level1_loc = (0.0, 0.0, 2.0)
level2_dim = (3.0, 2.0, 0.3)
level2_loc = (4.5, 0.0, 4.0)
level3_dim = (2.0, 1.0, 0.3)
level3_loc = (8.0, 0.0, 6.0)
col_cross = (0.5, 0.5)
col_full_height = 2.0
col1_scale_z = 0.8
col1_loc = (0.0, 0.0, 1.05)
col2_scale_z = 0.85
col2_loc = (4.5, 0.0, 3.0)
col3_scale_z = 0.85
col3_loc = (8.0, 0.0, 5.0)
load_dim = (0.5, 0.5, 0.5)
load_mass = 500.0
load_loc = (8.0, 0.0, 6.4)
sim_frames = 100

# Helper function to add rigid body
def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.linear_damping = 0.1
    obj.rigid_body.angular_damping = 0.1

# Helper to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.disable_collisions = True

# 1. Create Base (passive anchor)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "Base"
add_rigidbody(base, 'PASSIVE')

# 2. Create Level 1
bpy.ops.mesh.primitive_cube_add(size=1, location=level1_loc)
level1 = bpy.context.active_object
level1.scale = level1_dim
level1.name = "Level1"
add_rigidbody(level1)

# 3. Create Level 2
bpy.ops.mesh.primitive_cube_add(size=1, location=level2_loc)
level2 = bpy.context.active_object
level2.scale = level2_dim
level2.name = "Level2"
add_rigidbody(level2)

# 4. Create Level 3
bpy.ops.mesh.primitive_cube_add(size=1, location=level3_loc)
level3 = bpy.context.active_object
level3.scale = level3_dim
level3.name = "Level3"
add_rigidbody(level3)

# 5. Create Columns (scaled from default 2x2x2 cube)
# Column 1: Base to Level1
bpy.ops.mesh.primitive_cube_add(size=1, location=col1_loc)
col1 = bpy.context.active_object
col1.scale = (col_cross[0]/2, col_cross[1]/2, col_full_height/2 * col1_scale_z)
col1.name = "Column1"
add_rigidbody(col1)

# Column 2: Level1 to Level2
bpy.ops.mesh.primitive_cube_add(size=1, location=col2_loc)
col2 = bpy.context.active_object
col2.scale = (col_cross[0]/2, col_cross[1]/2, col_full_height/2 * col2_scale_z)
col2.name = "Column2"
add_rigidbody(col2)

# Column 3: Level2 to Level3
bpy.ops.mesh.primitive_cube_add(size=1, location=col3_loc)
col3 = bpy.context.active_object
col3.scale = (col_cross[0]/2, col_cross[1]/2, col_full_height/2 * col3_scale_z)
col3.name = "Column3"
add_rigidbody(col3)

# 6. Create Load (500kg mass)
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.scale = load_dim
load.name = "Load"
add_rigidbody(load, 'ACTIVE', load_mass)

# 7. Establish Fixed Constraints
# Base ↔ Column1 ↔ Level1
add_fixed_constraint(base, col1)
add_fixed_constraint(col1, level1)
# Level1 ↔ Column2 ↔ Level2
add_fixed_constraint(level1, col2)
add_fixed_constraint(col2, level2)
# Level2 ↔ Column3 ↔ Level3
add_fixed_constraint(level2, col3)
add_fixed_constraint(col3, level3)
# Load fixed to Level3
add_fixed_constraint(level3, load)

# 8. Setup physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = sim_frames

print("Stepped cantilever structure created with fixed constraints.")
print(f"Simulation will run for {sim_frames} frames.")