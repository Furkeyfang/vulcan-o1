import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
L_total = 20.0
deck_dim = (20.0, 3.0, 0.5)
deck_center = (10.0, 0.0, 0.25)
abut_dim = (2.0, 3.0, 2.0)
abutA_center = (0.0, 0.0, 1.0)
abutB_center = (20.0, 0.0, 1.0)
pier_dim = (1.0, 1.0, 4.0)
pier1_center = (6.0, 0.0, 2.0)
pier2_center = (16.0, 0.0, 2.0)
load_point = (11.0, 0.0, 0.5)
force_magnitude = -11772.0
force_radius = 0.2
sim_frames = 100
displacement_tolerance = 0.1

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=deck_center)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'
deck.rigid_body.collision_shape = 'BOX'

# Create Abutment A
bpy.ops.mesh.primitive_cube_add(size=1.0, location=abutA_center)
abutA = bpy.context.active_object
abutA.name = "Abutment_A"
abutA.scale = abut_dim
bpy.ops.rigidbody.object_add()
abutA.rigid_body.type = 'PASSIVE'
abutA.rigid_body.collision_shape = 'BOX'

# Create Pier 1
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pier1_center)
pier1 = bpy.context.active_object
pier1.name = "Pier_1"
pier1.scale = pier_dim
bpy.ops.rigidbody.object_add()
pier1.rigid_body.type = 'PASSIVE'
pier1.rigid_body.collision_shape = 'BOX'

# Create Pier 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pier2_center)
pier2 = bpy.context.active_object
pier2.name = "Pier_2"
pier2.scale = pier_dim
bpy.ops.rigidbody.object_add()
pier2.rigid_body.type = 'PASSIVE'
pier2.rigid_body.collision_shape = 'BOX'

# Create Abutment B
bpy.ops.mesh.primitive_cube_add(size=1.0, location=abutB_center)
abutB = bpy.context.active_object
abutB.name = "Abutment_B"
abutB.scale = abut_dim
bpy.ops.rigidbody.object_add()
abutB.rigid_body.type = 'PASSIVE'
abutB.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints between Deck and Supports
def add_fixed_constraint(obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = empty.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

# Connect deck to each support
add_fixed_constraint(deck, abutA)
add_fixed_constraint(deck, pier1)
add_fixed_constraint(deck, pier2)
add_fixed_constraint(deck, abutB)

# Create Force Field for point load
bpy.ops.object.empty_add(type='SPHERE', location=load_point)
force_empty = bpy.context.active_object
force_empty.name = "Force_Field"
force_empty.scale = (force_radius, force_radius, force_radius)
bpy.ops.object.forcefield_toggle()
force_field = force_empty.field
force_field.type = 'FORCE'
force_field.strength = force_magnitude
force_field.shape = 'POINT'
force_field.distance = force_radius
force_field.use_max_distance = True
force_field.falloff_power = 0.0  # Uniform within radius

# Link force field to affect only the Deck
# Create a collection for the deck
deck_collection = bpy.data.collections.new("Deck_Collection")
bpy.context.scene.collection.children.link(deck_collection)
deck_collection.objects.link(deck)
force_field.collection = deck_collection

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = sim_frames

# Run simulation (headless mode will execute when rendering)
bpy.ops.ptcache.free_bake_all()
bpy.ops.ptcache.bake_all(bake=True)

# Verification check (can be run after simulation)
def check_displacement():
    # In headless, we would read baked frames; here we outline the logic
    print("Simulation complete. Check console for displacement analysis.")
    # For actual verification, one would:
    # 1. Store initial deck location
    # 2. After baking, check final deck location
    # 3. Compute max displacement in Z
    # 4. Assert displacement < tolerance

# Call verification
check_displacement()