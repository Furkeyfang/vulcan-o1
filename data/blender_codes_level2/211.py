import bpy
import math
from mathutils import Vector, Euler

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
span_x = 10.0
peak_height = 3.0
top_end_height = 2.0
bottom_height = 1.0
top_chord_length = 5.5
bottom_chord_length = 5.5
diagonal_length = 3.5
top_chord_cross = (0.15, 0.15)
diagonal_cross = (0.1, 0.1)
load_force = 8338.65
top_chord_force_per_member = load_force / 2  # Two top chords

# Helper function to create a beam member
def create_beam(name, length, cross_section, location, rotation_euler):
    """Create a cube-based beam with given dimensions, location, and rotation."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    # Scale: length in X, cross_section in Y and Z
    beam.scale = (length / 2.0, cross_section[0] / 2.0, cross_section[1] / 2.0)
    beam.rotation_euler = rotation_euler
    # Add rigid body physics (active by default)
    bpy.ops.rigidbody.object_add()
    return beam

# Create top chords (left and right)
# Left top chord: from peak (0,3) to left top end (-5,2)
# Vector from peak to left end: (-5, -1, 0)
vec_left_top = Vector((-5.0, 0, top_end_height - peak_height))
length_left_top = vec_left_top.length  # Should be ~5.099
# We want the cube's local X axis to align with this vector
# Rotation: around Y axis? Actually, the vector is in XZ plane.
angle_y = math.atan2(vec_left_top.z, vec_left_top.x)  # Rotation around Y
# Cube's default X axis is (1,0,0). We rotate by angle_y around Y to align.
# But note: the cube's length is along X. After rotation, the cube's ends will be at ±(length/2,0,0) in local coords.
# We want the cube center at midpoint.
mid_left_top = Vector((-2.5, 0, 2.5))
beam_left_top = create_beam(
    "TopChord_Left",
    top_chord_length,
    top_chord_cross,
    mid_left_top,
    Euler((0, angle_y, 0), 'XYZ')
)

# Right top chord: from peak to right top end (5,2)
vec_right_top = Vector((5.0, 0, top_end_height - peak_height))
angle_y_right = math.atan2(vec_right_top.z, vec_right_top.x)
mid_right_top = Vector((2.5, 0, 2.5))
beam_right_top = create_beam(
    "TopChord_Right",
    top_chord_length,
    top_chord_cross,
    mid_right_top,
    Euler((0, angle_y_right, 0), 'XYZ')
)

# Create bottom chords (left and right)
# Left bottom chord: from bottom center (0,1) to left bottom end (-5,1)
vec_left_bottom = Vector((-5.0, 0, 0))
angle_y_bottom = math.atan2(vec_left_bottom.z, vec_left_bottom.x)  # 0?
mid_left_bottom = Vector((-2.5, 0, bottom_height))
beam_left_bottom = create_beam(
    "BottomChord_Left",
    bottom_chord_length,
    top_chord_cross,
    mid_left_bottom,
    Euler((0, angle_y_bottom, 0), 'XYZ')
)
# Make bottom chords passive (fixed supports)
beam_left_bottom.rigid_body.type = 'PASSIVE'

# Right bottom chord
vec_right_bottom = Vector((5.0, 0, 0))
angle_y_bottom_r = math.atan2(vec_right_bottom.z, vec_right_bottom.x)
mid_right_bottom = Vector((2.5, 0, bottom_height))
beam_right_bottom = create_beam(
    "BottomChord_Right",
    bottom_chord_length,
    top_chord_cross,
    mid_right_bottom,
    Euler((0, angle_y_bottom_r, 0), 'XYZ')
)
beam_right_bottom.rigid_body.type = 'PASSIVE'

# Create diagonal braces (four)
# Diagonal A (left): from top left (-5,2) to bottom center (0,1)
p1 = Vector((-5.0, 0, top_end_height))
p2 = Vector((0.0, 0, bottom_height))
vec_diagA = p2 - p1
mid_diagA = (p1 + p2) / 2
angle_y_diagA = math.atan2(vec_diagA.z, vec_diagA.x)
beam_diagA = create_beam(
    "Diagonal_A_Left",
    diagonal_length,
    diagonal_cross,
    mid_diagA,
    Euler((0, angle_y_diagA, 0), 'XYZ')
)

# Diagonal B (left): from bottom left (-5,1) to peak (0,3)
p3 = Vector((-5.0, 0, bottom_height))
p4 = Vector((0.0, 0, peak_height))
vec_diagB = p4 - p3
mid_diagB = (p3 + p4) / 2
angle_y_diagB = math.atan2(vec_diagB.z, vec_diagB.x)
beam_diagB = create_beam(
    "Diagonal_B_Left",
    diagonal_length,
    diagonal_cross,
    mid_diagB,
    Euler((0, angle_y_diagB, 0), 'XYZ')
)

# Diagonal A (right): from top right (5,2) to bottom center (0,1)
p5 = Vector((5.0, 0, top_end_height))
p6 = Vector((0.0, 0, bottom_height))
vec_diagA_r = p6 - p5  # Note: direction from top right to bottom center
mid_diagA_r = (p5 + p6) / 2
angle_y_diagA_r = math.atan2(vec_diagA_r.z, vec_diagA_r.x)
beam_diagA_r = create_beam(
    "Diagonal_A_Right",
    diagonal_length,
    diagonal_cross,
    mid_diagA_r,
    Euler((0, angle_y_diagA_r, 0), 'XYZ')
)

# Diagonal B (right): from bottom right (5,1) to peak (0,3)
p7 = Vector((5.0, 0, bottom_height))
p8 = Vector((0.0, 0, peak_height))
vec_diagB_r = p8 - p7
mid_diagB_r = (p7 + p8) / 2
angle_y_diagB_r = math.atan2(vec_diagB_r.z, vec_diagB_r.x)
beam_diagB_r = create_beam(
    "Diagonal_B_Right",
    diagonal_length,
    diagonal_cross,
    mid_diagB_r,
    Euler((0, angle_y_diagB_r, 0), 'XYZ')
)

# Create FIXED constraints between members at joints
def add_fixed_constraint(obj_a, obj_b, location):
    """Add a fixed rigid body constraint between two objects at a given location."""
    # Create an empty at joint location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    # Add rigid body constraint to empty
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    # Constraint location is already at empty location

# Define joint locations (as computed earlier)
joints = {
    "peak": Vector((0,0,peak_height)),
    "top_left": Vector((-5,0,top_end_height)),
    "top_right": Vector((5,0,top_end_height)),
    "bottom_center": Vector((0,0,bottom_height)),
    "bottom_left": Vector((-5,0,bottom_height)),
    "bottom_right": Vector((5,0,bottom_height)),
}

# Add constraints for each joint (connect relevant members)
# Peak: left top, right top, left diagonal B, right diagonal B
add_fixed_constraint(beam_left_top, beam_right_top, joints["peak"])
add_fixed_constraint(beam_left_top, beam_diagB, joints["peak"])
add_fixed_constraint(beam_left_top, beam_diagB_r, joints["peak"])

# Top left: left top, diagonal A left, diagonal B left
add_fixed_constraint(beam_left_top, beam_diagA, joints["top_left"])
add_fixed_constraint(beam_left_top, beam_diagB, joints["top_left"])

# Top right: right top, diagonal A right, diagonal B right
add_fixed_constraint(beam_right_top, beam_diagA_r, joints["top_right"])
add_fixed_constraint(beam_right_top, beam_diagB_r, joints["top_right"])

# Bottom center: left bottom, right bottom, diagonal A left, diagonal A right
add_fixed_constraint(beam_left_bottom, beam_right_bottom, joints["bottom_center"])
add_fixed_constraint(beam_left_bottom, beam_diagA, joints["bottom_center"])
add_fixed_constraint(beam_left_bottom, beam_diagA_r, joints["bottom_center"])

# Bottom left: left bottom, diagonal B left
add_fixed_constraint(beam_left_bottom, beam_diagB, joints["bottom_left"])

# Bottom right: right bottom, diagonal B right
add_fixed_constraint(beam_right_bottom, beam_diagB_r, joints["bottom_right"])

# Apply distributed load as a force field on top chords
# Create a force field (wind) pointing downward
bpy.ops.object.effector_add(type='FORCE', location=(0,0,2.5))
force_field = bpy.context.active_object
force_field.name = "RoofLoad"
force_field.field.strength = -top_chord_force_per_member  # Negative Z
force_field.field.falloff_power = 0  # Uniform
force_field.field.use_max_distance = True
force_field.field.distance_max = 1.0  # Affect only nearby objects
# Link force field to a collection containing only top chords
top_chord_collection = bpy.data.collections.new("TopChords")
bpy.context.scene.collection.children.link(top_chord_collection)
top_chord_collection.objects.link(beam_left_top)
top_chord_collection.objects.link(beam_right_top)
# Set force field to affect only this collection
force_field.field.affected_collection = top_chord_collection

# Set world gravity
bpy.context.scene.gravity = (0, 0, -9.81)

# Set rigid body world settings for stable simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Optional: Add a ground plane for visual reference
bpy.ops.mesh.primitive_plane_add(size=20, location=(0,0,-0.5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print("Scissor truss construction complete. Load applied.")