import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
deck_dim = (6.0, 3.0, 0.5)
deck_loc = (0.0, 0.0, 0.25)
beam_dim = (0.5, 0.5, 1.0)
beam_z_center = -0.5
num_beams = 5
beam_start_x = -2.75
beam_spacing_x = 1.375
load_dim = (1.0, 1.0, 1.0)
load_mass = 800.0
load_loc = (0.0, 0.0, 1.0)
ground_size = 20.0
sim_frames = 100

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True

# Create ground plane (passive)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create deck (passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=deck_loc)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = deck_dim
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'

# Create support beams (passive)
beam_objects = []
for i in range(num_beams):
    x_pos = beam_start_x + i * beam_spacing_x
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0.0, beam_z_center))
    beam = bpy.context.active_object
    beam.name = f"Beam_{i}"
    beam.scale = beam_dim
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam_objects.append(beam)
    
    # Add fixed constraint between beam and deck
    bpy.context.view_layer.objects.active = deck
    deck.select_set(True)
    beam.select_set(True)
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"Fix_Beam{i}_Deck"
    # Deselect for next iteration
    beam.select_set(False)
    deck.select_set(False)

# Create load cube (active, mass=800)
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Fixed constraint between load and deck
bpy.context.view_layer.objects.active = deck
deck.select_set(True)
load.select_set(True)
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint = bpy.context.active_object
constraint.name = "Fix_Load_Deck"

# Deselect all
bpy.ops.object.select_all(action='DESELECT')

# Set simulation length
bpy.context.scene.frame_end = sim_frames

# Optional: Bake simulation for verification (headless compatible)
# bpy.context.scene.rigidbody_world.point_cache.frame_end = sim_frames
# bpy.ops.ptcache.bake_all(bake=True)