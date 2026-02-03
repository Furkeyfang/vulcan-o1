import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span_length = 8.0
bridge_width = 2.0
truss_height = 1.5
chord_length = 8.0
chord_cross_section = (0.2, 0.2)
member_cross_section = (0.2, 0.2)
diag_length = 1.732
vertical_count = 11
diag_count = 9
unit_spacing = 0.866
left_truss_y = -1.0
right_truss_y = 1.0
top_chord_z = 1.5
bottom_chord_z = 0.0
ground_support_size = 0.5
ground_support_z = -0.25
load_mass = 500.0
gravity = 9.8

# Generate X positions for vertical members (including endpoints)
x_positions = [i * unit_spacing for i in range(diag_count + 2)]  # 0 to 9*0.866 = 7.794
# Adjust last position to exactly 8.0 for symmetry
x_positions[-1] = span_length

# Function to create a beam with rigid body
def create_beam(name, location, scale, rotation=(0,0,0), mass=1.0, active=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    # Apply rotation
    obj.rotation_euler = rotation
    # Apply rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE' if active else 'PASSIVE'
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b):
    # Select obj_a
    bpy.context.view_layer.objects.active = obj_a
    obj_a.select_set(True)
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.constraints[-1]
    const.type = 'FIXED'
    const.object2 = obj_b

# Create ground supports (passive)
supports = []
for x in [0.0, span_length]:
    for y in [left_truss_y, right_truss_y]:
        sup = create_beam(
            f"Support_{x}_{y}",
            (x, y, ground_support_z),
            (ground_support_size, ground_support_size, ground_support_size),
            active=False
        )
        supports.append(sup)

# Create trusses
trusses_y = [left_truss_y, right_truss_y]
all_chords = []
all_verticals = []
all_diagonals = []

for truss_idx, y in enumerate(trusses_y):
    side = "Left" if y < 0 else "Right"
    
    # Top chord (long beam)
    top_chord = create_beam(
        f"{side}_TopChord",
        (span_length/2, y, top_chord_z),
        (chord_length, chord_cross_section[0], chord_cross_section[1]),
        mass=load_mass/4  # Distributed mass for load simulation
    )
    all_chords.append(top_chord)
    
    # Bottom chord
    bottom_chord = create_beam(
        f"{side}_BottomChord",
        (span_length/2, y, bottom_chord_z),
        (chord_length, chord_cross_section[0], chord_cross_section[1]),
        mass=10.0
    )
    all_chords.append(bottom_chord)
    
    # Vertical members
    verticals = []
    for i, x in enumerate(x_positions):
        v = create_beam(
            f"{side}_Vertical_{i}",
            (x, y, (top_chord_z + bottom_chord_z)/2),
            (member_cross_section[0], member_cross_section[1], truss_height),
            mass=5.0
        )
        verticals.append(v)
        # Constraints to chords
        create_fixed_constraint(v, top_chord)
        create_fixed_constraint(v, bottom_chord)
    all_verticals.extend(verticals)
    
    # Diagonal members (alternating pattern)
    diagonals = []
    for i in range(diag_count):
        x_start = x_positions[i]
        x_end = x_positions[i+1]
        # Alternate direction: even i goes from bottom-start to top-end
        if i % 2 == 0:
            start_z = bottom_chord_z
            end_z = top_chord_z
        else:
            start_z = top_chord_z
            end_z = bottom_chord_z
        
        # Calculate center position and rotation
        center_x = (x_start + x_end) / 2
        center_z = (start_z + end_z) / 2
        length_3d = math.sqrt((x_end - x_start)**2 + (end_z - start_z)**2)
        # Rotation around Y axis: atan2(dz, dx)
        angle = math.atan2(end_z - start_z, x_end - x_start)
        
        diag = create_beam(
            f"{side}_Diagonal_{i}",
            (center_x, y, center_z),
            (length_3d, member_cross_section[0], member_cross_section[1]),
            rotation=(0, angle, 0),
            mass=7.0
        )
        diagonals.append(diag)
        # Constraints to chords (at endpoints)
        # We approximate by constraining to nearest vertical/chord intersection
        # For simplicity, constrain to the verticals at the ends
        create_fixed_constraint(diag, verticals[i])
        create_fixed_constraint(diag, verticals[i+1])
    all_diagonals.extend(diagonals)

# Constrain bottom chords to ground supports
for chord in all_chords:
    if "Bottom" in chord.name:
        for sup in supports:
            if abs(sup.location.x - chord.location.x) < 0.1 and abs(sup.location.y - chord.location.y) < 0.1:
                create_fixed_constraint(chord, sup)

# Set world gravity
if bpy.context.scene.rigidbody_world:
    bpy.context.scene.rigidbody_world.gravity.z = -gravity

print("Warren Truss bridge construction complete.")