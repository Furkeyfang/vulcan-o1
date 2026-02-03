import bpy
import mathutils
from mathutils import Vector

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
deck_dim = (7.0, 3.0, 0.1)
deck_pos = (0.0, 0.0, 0.5)

chord_len = 7.0
chord_w = 0.2
chord_h = 0.2
top_z = 0.5
bottom_z = 0.0
truss_y_left = -1.5
truss_y_right = 1.5

vert_count = 6
vert_spacing = 1.4
vert_w = 0.2
vert_d = 0.2
vert_h = 0.5

diag_count = 10
diag_w = 0.2
diag_d = 0.2
diag_len = 1.4866

pier_s = 0.5
pier_h = 0.5
pier_z = -0.25

load_mass = 1000.0
load_dim = (1.0, 1.0, 0.5)
load_pos = (3.5, 0.0, 0.6)

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj1, obj2, name="FixedJoint"):
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    constraint = bpy.context.active_object
    constraint.name = name
    constraint.empty_display_size = 0.2
    constraint.location = (0, 0, 0)
    
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    return constraint

# Create rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = bpy.data.collections.get('Collection')

# 1. CREATE DECK
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, deck_pos[2]))
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = (deck_dim[0]/2, deck_dim[1]/2, deck_dim[2]/2)
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'PASSIVE'

# 2. CREATE TOP AND BOTTOM CHORDS (left and right trusses)
chords = []
for y_pos in [truss_y_left, truss_y_right]:
    # Top chord
    bpy.ops.mesh.primitive_cube_add(size=1, location=(chord_len/2, y_pos, top_z))
    top_chord = bpy.context.active_object
    top_chord.name = f"TopChord_{'L' if y_pos<0 else 'R'}"
    top_chord.scale = (chord_len/2, chord_w/2, chord_h/2)
    bpy.ops.rigidbody.object_add()
    top_chord.rigid_body.type = 'PASSIVE'
    chords.append(top_chord)
    
    # Bottom chord
    bpy.ops.mesh.primitive_cube_add(size=1, location=(chord_len/2, y_pos, bottom_z))
    bottom_chord = bpy.context.active_object
    bottom_chord.name = f"BottomChord_{'L' if y_pos<0 else 'R'}"
    bottom_chord.scale = (chord_len/2, chord_w/2, chord_h/2)
    bpy.ops.rigidbody.object_add()
    bottom_chord.rigid_body.type = 'PASSIVE'
    chords.append(bottom_chord)

# 3. CREATE VERTICAL MEMBERS
verticals = []
for y_pos in [truss_y_left, truss_y_right]:
    for i in range(vert_count):
        x_pos = i * vert_spacing
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, y_pos, bottom_z + vert_h/2))
        vert = bpy.context.active_object
        vert.name = f"Vertical_{'L' if y_pos<0 else 'R'}_{i}"
        vert.scale = (vert_w/2, vert_d/2, vert_h/2)
        bpy.ops.rigidbody.object_add()
        vert.rigid_body.type = 'PASSIVE'
        verticals.append(vert)

# 4. CREATE DIAGONAL MEMBERS
diagonals = []
for y_pos in [truss_y_left, truss_y_right]:
    for i in range(vert_count-1):
        # Two diagonals per bay (alternating pattern)
        for diag_type in [0, 1]:
            if diag_type == 0:  # Top of i to bottom of i+1
                p1 = Vector((i*vert_spacing, y_pos, top_z))
                p2 = Vector(((i+1)*vert_spacing, y_pos, bottom_z))
            else:  # Bottom of i to top of i+1
                p1 = Vector((i*vert_spacing, y_pos, bottom_z))
                p2 = Vector(((i+1)*vert_spacing, y_pos, top_z))
            
            mid = (p1 + p2) / 2
            direction = (p2 - p1).normalized()
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
            diag = bpy.context.active_object
            diag.name = f"Diagonal_{'L' if y_pos<0 else 'R'}_{i}_{diag_type}"
            diag.scale = (diag_w/2, diag_d/2, diag_len/2)
            
            # Rotate to align with direction vector
            up = Vector((0, 0, 1))
            rotation = up.rotation_difference(direction)
            diag.rotation_euler = rotation.to_euler()
            
            bpy.ops.rigidbody.object_add()
            diag.rigid_body.type = 'PASSIVE'
            diagonals.append(diag)

# 5. CREATE GROUND PIERS
piers = []
pier_locations = [
    (0, truss_y_left, pier_z),
    (chord_len, truss_y_left, pier_z),
    (0, truss_y_right, pier_z),
    (chord_len, truss_y_right, pier_z)
]

for i, (x, y, z) in enumerate(pier_locations):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    pier = bpy.context.active_object
    pier.name = f"Pier_{i}"
    pier.scale = (pier_s/2, pier_s/2, pier_h/2)
    bpy.ops.rigidbody.object_add()
    pier.rigid_body.type = 'PASSIVE'
    piers.append(pier)

# 6. CREATE LOAD CUBE
bpy.ops.mesh.primitive_cube_add(size=1, location=load_pos)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# 7. CREATE FIXED CONSTRAINTS
constraints = []

# Connect piers to bottom chords
for pier in piers:
    # Find corresponding bottom chord (same X and Y)
    for chord in chords:
        if "BottomChord" in chord.name:
            if abs(chord.location.x - pier.location.x) < 0.1 and abs(chord.location.y - pier.location.y) < 0.1:
                constraints.append(create_fixed_constraint(pier, chord, f"PierToChord_{pier.name}"))

# Connect verticals to chords
for vert in verticals:
    y_pos = vert.location.y
    x_pos = vert.location.x
    
    # Find corresponding chords
    for chord in chords:
        if abs(chord.location.y - y_pos) < 0.1:
            if "BottomChord" in chord.name and abs(vert.location.z - (bottom_z + vert_h/2)) < 0.1:
                if abs(x_pos - chord.location.x) < chord_len/2 + 0.1:
                    constraints.append(create_fixed_constraint(vert, chord, f"VertToBottom_{vert.name}"))
            elif "TopChord" in chord.name and abs(vert.location.z + vert_h/2 - top_z) < 0.1:
                if abs(x_pos - chord.location.x) < chord_len/2 + 0.1:
                    constraints.append(create_fixed_constraint(vert, chord, f"VertToTop_{vert.name}"))

# Connect diagonals to chords and verticals
for diag in diagonals:
    # Get endpoints from diagonal's transform
    diag_matrix = diag.matrix_world
    local_end = Vector((0, 0, diag_len/2))
    world_end1 = diag_matrix @ local_end
    world_end2 = diag_matrix @ -local_end
    
    # Connect to nearest chords/verticals
    for obj in chords + verticals:
        if abs(obj.location.y - diag.location.y) < 0.1:
            dist1 = (obj.location - world_end1).length
            dist2 = (obj.location - world_end2).length
            if min(dist1, dist2) < 0.2:  # Within connection tolerance
                constraints.append(create_fixed_constraint(diag, obj, f"DiagTo_{diag.name}_{obj.name}"))

# Connect deck to top chords
for chord in chords:
    if "TopChord" in chord.name:
        constraints.append(create_fixed_constraint(deck, chord, f"DeckTo_{chord.name}"))

# Set simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Howe Truss ramp construction complete. Simulation ready for 100 frames.")