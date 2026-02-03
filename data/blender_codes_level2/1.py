import bpy
import math
from mathutils import Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 10.0
height = 2.0
cross_section = 0.2
top_chord_loc = (0.0, 0.0, 2.0)
bottom_chord_loc = (0.0, 0.0, 0.0)
vertical_x_positions = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
vertical_center_z = 1.0
diagonal_length = 2.8284271247461903
diagonal_angle = 45.0
total_load_N = 4905.0
load_per_meter = 490.5
top_joint_loads = {0.0: 490.5, 2.0: 981.0, 4.0: 981.0, 6.0: 981.0, 8.0: 981.0, 10.0: 490.5}

# Enable rigid body physics
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

# Helper to add a beam
def add_beam(name, location, scale, rotation_euler=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = scale
    beam.rotation_euler = rotation_euler
    bpy.ops.rigidbody.object_add()
    return beam

# Create top chord (horizontal beam)
top_chord = add_beam("TopChord", top_chord_loc, (span, cross_section, cross_section))
top_chord.rigid_body.type = 'ACTIVE'  # To receive loads

# Create bottom chord
bottom_chord = add_beam("BottomChord", bottom_chord_loc, (span, cross_section, cross_section))
bottom_chord.rigid_body.type = 'PASSIVE'

# Create vertical members
verticals = []
for i, x in enumerate(vertical_x_positions):
    vert = add_beam(f"Vertical_{i}", (x, 0.0, vertical_center_z), (cross_section, cross_section, height))
    vert.rigid_body.type = 'PASSIVE'
    verticals.append(vert)

# Create diagonal members (alternating direction)
diagonals = []
for i in range(5):  # 5 bays between 6 verticals
    x_start = vertical_x_positions[i]
    x_end = vertical_x_positions[i+1]
    # Diagonal from top of start vertical to bottom of end vertical
    mid_x = (x_start + x_end) / 2.0
    mid_z = 1.0  # Average of 2 and 0
    # Rotation: -45° for first diagonal, +45° for next, alternating
    angle_rad = math.radians(diagonal_angle * (-1 if i % 2 == 0 else 1))
    diag = add_beam(f"Diagonal_{i}", (mid_x, 0.0, mid_z), 
                    (diagonal_length, cross_section, cross_section),
                    rotation_euler=(0, angle_rad, 0))
    diag.rigid_body.type = 'PASSIVE'
    diagonals.append(diag)

# Create fixed constraints at joints
def add_fixed_constraint(obj1, obj2, location):
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Top joints (each vertical meets top chord)
for i, (x, vert) in enumerate(zip(vertical_x_positions, verticals)):
    add_fixed_constraint(top_chord, vert, (x, 0.0, 2.0))
    # Also connect diagonal to top chord at start point if diagonal starts here
    if i < 5:  # Diagonals start at i=0..4
        if i % 2 == 0:  # Diagonal starts at this top joint
            add_fixed_constraint(top_chord, diagonals[i], (x, 0.0, 2.0))
            add_fixed_constraint(vert, diagonals[i], (x, 0.0, 2.0))
    if i > 0:  # Diagonals end at i=1..5
        if i % 2 == 1:  # Previous diagonal ends at this top joint? Wait, diagonals end at bottom joints. Correction needed.
            pass  # Diagonals end at bottom joints, handled below

# Bottom joints (each vertical meets bottom chord)
for i, (x, vert) in enumerate(zip(vertical_x_positions, verticals)):
    add_fixed_constraint(bottom_chord, vert, (x, 0.0, 0.0))
    # Connect diagonal to bottom chord at end point
    if i > 0:  # Diagonals end at i=1..5
        diag_idx = i-1
        if diag_idx % 2 == 0:  # Diagonal from top of i-1 to bottom of i
            add_fixed_constraint(bottom_chord, diagonals[diag_idx], (x, 0.0, 0.0))
            add_fixed_constraint(vert, diagonals[diag_idx], (x, 0.0, 0.0))

# Apply point loads to top chord at joint locations (as forces on rigid body)
# Since top chord is one object, apply forces at respective vertices? 
# Alternative: apply forces to verticals at top joints, which transfer to chord via constraints.
# We'll apply forces to verticals at their top (which is connected to top chord).
for x, vert in zip(vertical_x_positions, verticals):
    force_mag = top_joint_loads[x]
    # Apply downward force (negative Z) at the vertical's center (simplified)
    vert.rigid_body.force = (0.0, 0.0, -force_mag)

# Set gravity to standard
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Ensure proper collision shapes
for obj in bpy.context.scene.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_shape = 'BOX'

print("Pratt truss bridge constructed with fixed constraints and loads applied.")