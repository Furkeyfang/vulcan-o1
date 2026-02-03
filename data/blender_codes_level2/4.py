import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
span_length = 6.0
deck_dim = (6.0, 2.0, 0.1)
deck_center = (3.0, 0.0, 0.5)
bottom_chord_dim = (6.0, 0.1, 0.1)
bottom_chord_center = (3.0, 0.0, 0.5)
top_chord_dim = (6.0, 0.1, 0.1)
top_chord_center = (3.0, 0.0, 1.5)
vertical_locations = [(0.0, 0.0, 1.0), (2.0, 0.0, 1.0), (4.0, 0.0, 1.0), (6.0, 0.0, 1.0)]
vertical_dim = (0.1, 0.1, 1.0)
diagonal_midpoints = [(1.0, 0.0, 1.0), (3.0, 0.0, 1.0), (5.0, 0.0, 1.0)]
diagonal_length = math.sqrt(5)  # ≈2.23607
diagonal_rotation = math.degrees(math.atan(-1/2))  # ≈-26.565°
support_centers = [(0.0, 0.0, 0.25), (6.0, 0.0, 0.25)]
support_dim = (0.2, 0.2, 0.5)
load_start = (0.5, 0.0, 0.8)
load_end = (5.5, 0.0, 0.8)
load_dim = (0.5, 0.5, 0.5)
load_mass = 300.0
total_frames = 200

# Helper function to create a cube with rigid body
def create_cube(name, location, scale, rigid_body_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    return obj

# Create supports
supports = []
for i, loc in enumerate(support_centers):
    sup = create_cube(f"Support_{i}", loc, support_dim)
    supports.append(sup)

# Create deck
deck = create_cube("Deck", deck_center, deck_dim)

# Create bottom chord
bottom_chord = create_cube("BottomChord", bottom_chord_center, bottom_chord_dim)

# Create top chord
top_chord = create_cube("TopChord", top_chord_center, top_chord_dim)

# Create vertical members
verticals = []
for i, loc in enumerate(vertical_locations):
    vert = create_cube(f"Vertical_{i}", loc, vertical_dim)
    verticals.append(vert)

# Create diagonal members
diagonals = []
for i, loc in enumerate(diagonal_midpoints):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    diag = bpy.context.active_object
    diag.name = f"Diagonal_{i}"
    diag.scale = (diagonal_length, 0.1, 0.1)
    diag.rotation_euler = (0.0, math.radians(diagonal_rotation), 0.0)
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'PASSIVE'
    diagonals.append(diag)

# Create moving load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_start)
load = bpy.context.active_object
load.name = "MovingLoad"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Animate load movement
load.location = load_start
load.keyframe_insert(data_path="location", frame=1)
load.location = load_end
load.keyframe_insert(data_path="location", frame=total_frames)

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Add fixed constraints between connected members
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.constraints[-1]
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# Bond deck to supports
for sup in supports:
    add_fixed_constraint(deck, sup)

# Bond bottom chord to supports
for sup in supports:
    add_fixed_constraint(bottom_chord, sup)

# Bond bottom chord to deck
add_fixed_constraint(bottom_chord, deck)

# Bond verticals to bottom and top chords
for vert in verticals:
    add_fixed_constraint(vert, bottom_chord)
    add_fixed_constraint(vert, top_chord)

# Bond diagonals to respective chords and verticals
# Diagonal 0 connects top at X=0 to bottom at X=2
add_fixed_constraint(diagonals[0], top_chord)
add_fixed_constraint(diagonals[0], bottom_chord)
add_fixed_constraint(diagonals[0], verticals[0])  # vertical at X=0
add_fixed_constraint(diagonals[0], verticals[1])  # vertical at X=2

# Diagonal 1 connects top at X=2 to bottom at X=4
add_fixed_constraint(diagonals[1], top_chord)
add_fixed_constraint(diagonals[1], bottom_chord)
add_fixed_constraint(diagonals[1], verticals[1])  # vertical at X=2
add_fixed_constraint(diagonals[1], verticals[2])  # vertical at X=4

# Diagonal 2 connects top at X=4 to bottom at X=6
add_fixed_constraint(diagonals[2], top_chord)
add_fixed_constraint(diagonals[2], bottom_chord)
add_fixed_constraint(diagonals[2], verticals[2])  # vertical at X=4
add_fixed_constraint(diagonals[2], verticals[3])  # vertical at X=6

# Set animation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = total_frames

print("Bridge construction complete. Ready for simulation.")