import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Define variables from parameter summary
deck_length = 14.0
deck_width = 2.0
deck_thickness = 0.3
deck_loc_z = 2.15

column_size_xy = 0.5
column_height = 2.0
column_left_x = -7.0
column_right_x = 7.0
column_loc_z = 1.0  # center of column (height/2)

load_cube_size = 0.5
load_mass = 600.0
load_loc_x = 0.0
load_loc_z = 2.55

ground_size = 30.0
simulation_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create bridge deck (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = (deck_length, deck_width, deck_thickness)
deck.location = (0, 0, deck_loc_z)
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.collision_shape = 'BOX'

# Create left column (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0)
col_left = bpy.context.active_object
col_left.name = "Column_Left"
col_left.scale = (column_size_xy, column_size_xy, column_height)
col_left.location = (column_left_x, 0, column_loc_z)
bpy.ops.rigidbody.object_add()
col_left.rigid_body.type = 'PASSIVE'
col_left.rigid_body.collision_shape = 'BOX'

# Create right column (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0)
col_right = bpy.context.active_object
col_right.name = "Column_Right"
col_right.scale = (column_size_xy, column_size_xy, column_height)
col_right.location = (column_right_x, 0, column_loc_z)
bpy.ops.rigidbody.object_add()
col_right.rigid_body.type = 'PASSIVE'
col_right.rigid_body.collision_shape = 'BOX'

# Create load cube (active rigid body with mass)
bpy.ops.mesh.primitive_cube_add(size=1.0)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_cube_size, load_cube_size, load_cube_size)
load.location = (load_loc_x, 0, load_loc_z)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between ground and columns
def add_fixed_constraint(obj_a, obj_b):
    """Create a fixed rigid body constraint between two objects."""
    # Create empty object for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    constraint.empty_display_size = 1.0
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj_a
    rb_constraint.object2 = obj_b
    # Lock all degrees of freedom
    rb_constraint.use_limit_lin_x = True
    rb_constraint.use_limit_lin_y = True
    rb_constraint.use_limit_lin_z = True
    rb_constraint.use_limit_ang_x = True
    rb_constraint.use_limit_ang_y = True
    rb_constraint.use_limit_ang_z = True
    rb_constraint.limit_lin_x_lower = 0
    rb_constraint.limit_lin_x_upper = 0
    rb_constraint.limit_lin_y_lower = 0
    rb_constraint.limit_lin_y_upper = 0
    rb_constraint.limit_lin_z_lower = 0
    rb_constraint.limit_lin_z_upper = 0
    rb_constraint.limit_ang_x_lower = 0
    rb_constraint.limit_ang_x_upper = 0
    rb_constraint.limit_ang_y_lower = 0
    rb_constraint.limit_ang_y_upper = 0
    rb_constraint.limit_ang_z_lower = 0
    rb_constraint.limit_ang_z_upper = 0

# Apply constraints
add_fixed_constraint(ground, col_left)
add_fixed_constraint(ground, col_right)
add_fixed_constraint(col_left, deck)
add_fixed_constraint(col_right, deck)

# Set simulation end frame
bpy.context.scene.frame_end = simulation_frames

# Optional: Set gravity to standard -9.81 m/s² (already default)
bpy.context.scene.gravity = (0, 0, -9.81)

# Bake the simulation (optional, for verification)
# bpy.ops.ptcache.bake_all(bake=True)

print("Bridge construction complete. Simulation ready.")