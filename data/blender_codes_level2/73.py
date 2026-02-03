import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
ground_size = (10.0, 10.0, 0.1)
ground_loc = (0.0, 0.0, -0.05)
column_dim = (0.5, 0.5, 3.0)
column_loc = (0.0, 0.0, 1.5)
beam_dim = (4.0, 2.0, 0.3)
beam_loc = (2.0, 0.0, 3.15)
deck_dim = (4.0, 2.0, 0.1)
deck_loc = (2.0, 0.0, 3.35)
load_dim = (0.5, 0.5, 0.5)
load_loc = (4.0, 0.0, 3.65)
load_mass = 400.0
sim_frames = 100

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create vertical column
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create horizontal beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'

# Create deck surface
bpy.ops.mesh.primitive_cube_add(size=1, location=deck_loc)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.type = 'ACTIVE'

# Create fixed constraints
def add_fixed_constraint(obj1, obj2, name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Column to ground constraint
add_fixed_constraint(ground, column, "Ground_Column_Constraint")

# Beam to column constraint
add_fixed_constraint(column, beam, "Column_Beam_Constraint")

# Deck to beam constraint
add_fixed_constraint(beam, deck, "Beam_Deck_Constraint")

# Load to deck constraint
add_fixed_constraint(deck, load, "Deck_Load_Constraint")

# Configure simulation
scene = bpy.context.scene
scene.rigidbody_world.enabled = True
scene.frame_end = sim_frames

# Run simulation
for frame in range(scene.frame_end + 1):
    scene.frame_set(frame)
    scene.update()