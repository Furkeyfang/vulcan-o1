import bpy
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 10.0
wall_height = 3.0
wall_thickness = 0.2
wall_width = 10.0
member_cross_section = 0.2
bottom_chord_length = 10.0
upper_chord1_length = 5.5
vertical1_length = 1.5
vertical2_length = 3.0
diagonal1_length = 3.354
diagonal2_length = 3.354
peak_height = 6.0
break_height = 4.5
break_offset = 2.5
total_load_N = 7848.0
bottom_chord_segments = 10
force_per_segment = 784.8
simulation_frames = 500

# Helper to create a beam (cube) scaled to length and cross-section
def create_beam(name, length, location, rotation_euler):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (length, member_cross_section, member_cross_section)
    beam.rotation_euler = rotation_euler
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    return beam

# Create support walls (Passive Rigid Bodies)
# Left wall: inner face at x=0, extends leftwards 10 m
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.0, 0.0, wall_height/2))
left_wall = bpy.context.active_object
left_wall.name = "LeftWall"
left_wall.scale = (wall_width, wall_thickness, wall_height)
bpy.ops.rigidbody.object_add()
left_wall.rigid_body.type = 'PASSIVE'

# Right wall: inner face at x=span, extends rightwards 10 m
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(span + 5.0, 0.0, wall_height/2))
right_wall = bpy.context.active_object
right_wall.name = "RightWall"
right_wall.scale = (wall_width, wall_thickness, wall_height)
bpy.ops.rigidbody.object_add()
right_wall.rigid_body.type = 'PASSIVE'

# Create truss members (all Active Rigid Bodies)
# Bottom chord (split into segments for distributed load)
bottom_chord_segment_length = bottom_chord_length / bottom_chord_segments
bottom_chord_objects = []
for i in range(bottom_chord_segments):
    x_center = (i + 0.5) * bottom_chord_segment_length
    loc = (x_center, 0.0, wall_height)
    bottom_chord = create_beam(f"BottomChord_{i}", bottom_chord_segment_length, loc, (0.0, 0.0, 0.0))
    bottom_chord_objects.append(bottom_chord)

# Upper chords (four segments total)
# Left lower chord: (0,0,3) to (2.5,0,4.5)
angle1 = math.atan2(break_height - wall_height, break_offset)
length1 = math.hypot(break_offset, break_height - wall_height)
upper_left_lower = create_beam("UpperLeftLower", length1, 
                               (break_offset/2, 0.0, wall_height + (break_height - wall_height)/2),
                               (0.0, -angle1, 0.0))

# Left upper chord: (2.5,0,4.5) to (5,0,6)
angle2 = math.atan2(peak_height - break_height, break_offset)
length2 = math.hypot(break_offset, peak_height - break_height)
upper_left_upper = create_beam("UpperLeftUpper", length2,
                               (break_offset*1.5, 0.0, break_height + (peak_height - break_height)/2),
                               (0.0, -angle2, 0.0))

# Right upper chord: (5,0,6) to (7.5,0,4.5) (symmetrical)
upper_right_upper = create_beam("UpperRightUpper", length2,
                                (span - break_offset*1.5, 0.0, break_height + (peak_height - break_height)/2),
                                (0.0, angle2, 0.0))

# Right lower chord: (7.5,0,4.5) to (10,0,3)
upper_right_lower = create_beam("UpperRightLower", length1,
                                (span - break_offset/2, 0.0, wall_height + (break_height - wall_height)/2),
                                (0.0, angle1, 0.0))

# Vertical web members
vertical1 = create_beam("Vertical1", vertical1_length,
                        (break_offset, 0.0, wall_height + vertical1_length/2),
                        (0.0, 0.0, 0.0))
vertical2 = create_beam("Vertical2", vertical2_length,
                        (span/2, 0.0, wall_height + vertical2_length/2),
                        (0.0, 0.0, 0.0))
vertical3 = create_beam("Vertical3", vertical1_length,
                        (span - break_offset, 0.0, wall_height + vertical1_length/2),
                        (0.0, 0.0, 0.0))

# Diagonal web members
diag1_angle = math.atan2(peak_height - wall_height, span/2 - break_offset)
diagonal1 = create_beam("Diagonal1", diagonal1_length,
                        ((break_offset + span/2)/2, 0.0, wall_height + (peak_height - wall_height)/2),
                        (0.0, -diag1_angle, 0.0))
diagonal2 = create_beam("Diagonal2", diagonal2_length,
                        ((span/2 + span - break_offset)/2, 0.0, wall_height + (peak_height - wall_height)/2),
                        (0.0, diag1_angle, 0.0))

# Collect all truss members for constraint creation
truss_members = bottom_chord_objects + [upper_left_lower, upper_left_upper, upper_right_upper, upper_right_lower,
                                        vertical1, vertical2, vertical3, diagonal1, diagonal2]

# Function to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    # Create empty for constraint (headless compatible)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_a.name}"
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Create constraints at joints
# Joint at (0,0,3): left wall inner face, first bottom chord segment, left lower upper chord
add_fixed_constraint(left_wall, bottom_chord_objects[0])
add_fixed_constraint(bottom_chord_objects[0], upper_left_lower)

# Joint at (2.5,0,3): bottom chord segment boundary, vertical1, diagonal1
add_fixed_constraint(bottom_chord_objects[2], bottom_chord_objects[3])  # segment junction
add_fixed_constraint(bottom_chord_objects[2], vertical1)
add_fixed_constraint(bottom_chord_objects[2], diagonal1)
add_fixed_constraint(vertical1, upper_left_lower)
add_fixed_constraint(vertical1, upper_left_upper)

# Joint at (2.5,0,4.5): upper_left_lower, upper_left_upper, vertical1
add_fixed_constraint(upper_left_lower, upper_left_upper)
# (vertical1 already connected)

# Joint at (5,0,3): bottom chord midpoint, vertical2, diagonal1, diagonal2
mid_segment = bottom_chord_objects[4]  # segment covering x=4.5-5.5
add_fixed_constraint(mid_segment, vertical2)
add_fixed_constraint(mid_segment, diagonal1)
add_fixed_constraint(mid_segment, diagonal2)

# Joint at (5,0,6): upper_left_upper, upper_right_upper, vertical2, diagonal1, diagonal2
add_fixed_constraint(upper_left_upper, upper_right_upper)
add_fixed_constraint(upper_left_upper, vertical2)
add_fixed_constraint(upper_left_upper, diagonal1)
add_fixed_constraint(upper_right_upper, diagonal2)

# Joint at (7.5,0,3): symmetric to (2.5,0,3)
add_fixed_constraint(bottom_chord_objects[6], bottom_chord_objects[7])
add_fixed_constraint(bottom_chord_objects[6], vertical3)
add_fixed_constraint(bottom_chord_objects[6], diagonal2)
add_fixed_constraint(vertical3, upper_right_lower)
add_fixed_constraint(vertical3, upper_right_upper)

# Joint at (7.5,0,4.5): upper_right_upper, upper_right_lower, vertical3
add_fixed_constraint(upper_right_upper, upper_right_lower)

# Joint at (10,0,3): right wall inner face, last bottom chord segment, right lower upper chord
add_fixed_constraint(right_wall, bottom_chord_objects[-1])
add_fixed_constraint(bottom_chord_objects[-1], upper_right_lower)

# Connect adjacent bottom chord segments (continuous beam)
for i in range(len(bottom_chord_objects)-1):
    add_fixed_constraint(bottom_chord_objects[i], bottom_chord_objects[i+1])

# Apply distributed load as downward force on each bottom chord segment
for seg in bottom_chord_objects:
    seg.rigid_body.use_gravity = True
    # Apply constant force (simulate distributed load)
    # In Blender, we can apply force via rigid body settings, but it's per-object constant force.
    seg.rigid_body.constant_force = (0.0, 0.0, -force_per_segment)

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Optional: Bake simulation for headless verification
# bpy.ops.ptcache.bake_all(bake=True)