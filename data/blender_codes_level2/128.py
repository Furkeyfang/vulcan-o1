import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
deck_dim = (6.0, 2.0, 0.5)
deck_loc = (3.0, 0.0, 0.25)
column_dim = (0.5, 0.5, 3.0)
column1_loc = (0.0, -0.75, 1.5)
column2_loc = (0.0, 0.75, 1.5)
ground_dim = (20.0, 20.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)
load_mass = 1000.0
load_size = (0.3, 0.3, 0.3)
load_loc = (6.0, 0.0, 0.5)
breaking_thresh = 10000.0

# Enable rigid body simulation
bpy.context.scene.rigidbody_world.enabled = True

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_dim
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create columns
bpy.ops.mesh.primitive_cube_add(size=1, location=column1_loc)
col1 = bpy.context.active_object
col1.name = "Column_Left"
col1.scale = column_dim
bpy.ops.rigidbody.object_add()
col1.rigid_body.type = 'PASSIVE'
col1.rigid_body.collision_shape = 'BOX'

bpy.ops.mesh.primitive_cube_add(size=1, location=column2_loc)
col2 = bpy.context.active_object
col2.name = "Column_Right"
col2.scale = column_dim
bpy.ops.rigidbody.object_add()
col2.rigid_body.type = 'PASSIVE'
col2.rigid_body.collision_shape = 'BOX'

# Create deck
bpy.ops.mesh.primitive_cube_add(size=1, location=deck_loc)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.collision_shape = 'BOX'

# Create load object
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_size
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between deck and columns
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj_a
    const.rigid_body_constraint.object2 = obj_b
    const.rigid_body_constraint.breaking_threshold = breaking_thresh

add_fixed_constraint(deck, col1)
add_fixed_constraint(deck, col2)

# Create fixed constraints between columns and ground
add_fixed_constraint(col1, ground)
add_fixed_constraint(col2, ground)

# Create fixed constraint between load and deck (simulates bonded load)
add_fixed_constraint(load, deck)

# Set simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Bake simulation for verification
bpy.ops.ptcache.bake_all(bake=True)

print("Cantilever bridge setup complete. Simulation baked for 100 frames.")
print(f"Load mass: {load_mass} kg, Constraint breaking threshold: {breaking_thresh} N")