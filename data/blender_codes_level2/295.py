import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
col_dim = (0.5, 0.5, 5.0)
col_loc = (0.0, 0.0, 2.5)
arm_x_dim = (4.0, 0.3, 0.3)
arm_x_loc = (2.0, 0.0, 4.85)
arm_y_dim = (7.0, 0.4, 0.4)
arm_y_loc = (0.0, 3.5, 4.8)
load1_rad = 0.5
load1_dep = 0.2
load1_mass = 300.0
load1_loc = (4.0, 0.0, 5.1)
load2_rad = 0.7
load2_dep = 0.3
load2_mass = 600.0
load2_loc = (0.0, 7.0, 5.15)
con_strength = 1000000.0
sim_frames = 100

# Create main column (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create X-axis arm (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_x_loc)
arm_x = bpy.context.active_object
arm_x.name = "Arm_X"
arm_x.scale = arm_x_dim
bpy.ops.rigidbody.object_add()
arm_x.rigid_body.type = 'PASSIVE'

# Create Y-axis arm (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_y_loc)
arm_y = bpy.context.active_object
arm_y.name = "Arm_Y"
arm_y.scale = arm_y_dim
bpy.ops.rigidbody.object_add()
arm_y.rigid_body.type = 'PASSIVE'

# Create Load1 (cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=load1_rad, depth=load1_dep, location=load1_loc)
load1 = bpy.context.active_object
load1.name = "Load_300kg"
bpy.ops.rigidbody.object_add()
load1.rigid_body.type = 'ACTIVE'
load1.rigid_body.mass = load1_mass

# Create Load2 (cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=load2_rad, depth=load2_dep, location=load2_loc)
load2 = bpy.context.active_object
load2.name = "Load_600kg"
bpy.ops.rigidbody.object_add()
load2.rigid_body.type = 'ACTIVE'
load2.rigid_body.mass = load2_mass

# Function to create fixed constraint between two objects at a given location
def create_fixed_constraint(obj_a, obj_b, con_loc, strength):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=con_loc)
    con = bpy.context.active_object
    con.name = f"Fixed_{obj_a.name}_to_{obj_b.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    con.rigid_body_constraint.type = 'FIXED'
    con.rigid_body_constraint.object1 = obj_a
    con.rigid_body_constraint.object2 = obj_b
    con.rigid_body_constraint.use_breaking = True
    con.rigid_body_constraint.breaking_threshold = strength
    con.rigid_body_constraint.use_override_solver_iterations = True
    con.rigid_body_constraint.solver_iterations = 50

# Create constraints
# Column to Arm_X at (0,0,5) - connection point
create_fixed_constraint(column, arm_x, (0.0, 0.0, 5.0), con_strength)
# Column to Arm_Y at (0,0,5)
create_fixed_constraint(column, arm_y, (0.0, 0.0, 5.0), con_strength)
# Arm_X to Load1 at load1_loc
create_fixed_constraint(arm_x, load1, load1_loc, con_strength)
# Arm_Y to Load2 at load2_loc
create_fixed_constraint(arm_y, load2, load2_loc, con_strength)

# Configure rigid body world for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Set simulation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = sim_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print("Double-cantilever beam system created and simulated.")