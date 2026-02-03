import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
deck_length = 18.0
deck_width = 3.0
deck_height = 0.5
deck_center_x = 9.0
deck_center_y = 0.0
deck_center_z = 5.25

column_width = 1.0
column_depth = 1.0
column_height = 5.0
column1_center_x = 5.0
column2_center_x = 13.0
column_center_y = 0.0
column_center_z = 2.5

load_size = 1.0
load_mass = 1000.0
load_center_x = 9.0
load_center_y = 0.0
load_center_z = 6.0

simulation_frames = 500

# Create passive ground plane (large cube)
bpy.ops.mesh.primitive_cube_add(size=50.0, location=(0,0,-0.5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create Column 1
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(column1_center_x, column_center_y, column_center_z))
col1 = bpy.context.active_object
col1.name = "Column1"
col1.scale = (column_width, column_depth, column_height)
bpy.ops.rigidbody.object_add()
col1.rigid_body.type = 'ACTIVE'
col1.rigid_body.collision_shape = 'BOX'
col1.rigid_body.mass = 100.0  # Estimated mass

# Create Column 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(column2_center_x, column_center_y, column_center_z))
col2 = bpy.context.active_object
col2.name = "Column2"
col2.scale = (column_width, column_depth, column_height)
bpy.ops.rigidbody.object_add()
col2.rigid_body.type = 'ACTIVE'
col2.rigid_body.collision_shape = 'BOX'
col2.rigid_body.mass = 100.0

# Create Bridge Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(deck_center_x, deck_center_y, deck_center_z))
deck = bpy.context.active_object
deck.name = "BridgeDeck"
deck.scale = (deck_length, deck_width, deck_height)
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'ACTIVE'
deck.rigid_body.collision_shape = 'BOX'
deck.rigid_body.mass = 500.0  # Estimated mass

# Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(load_center_x, load_center_y, load_center_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass

# Create Fixed Constraints
def add_fixed_constraint(obj1, obj2):
    """Create a fixed rigid body constraint between two objects."""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Column base constraints to ground
add_fixed_constraint(col1, ground)
add_fixed_constraint(col2, ground)

# Deck to column top constraints
add_fixed_constraint(deck, col1)
add_fixed_constraint(deck, col2)

# Configure simulation settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Ensure proper collision margins
for obj in [col1, col2, deck, load, ground]:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.0

print("Bridge assembly complete. Simulation ready for 500 frames.")