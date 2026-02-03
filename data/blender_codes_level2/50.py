import bpy
import math
from mathutils import Vector

# ------------------------------------------------------------
# 1. Clear existing scene
# ------------------------------------------------------------
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ------------------------------------------------------------
# 2. Define variables from parameter summary
# ------------------------------------------------------------
span_x = 12.0
width_y = 2.0
height_z = 3.0
standard_cross = 0.2
reinforced_cross = 0.3
vertical_interval = 2.0
bottom_z = 0.0
top_z = 3.0
truss_y_offset = width_y / 2.0  # = 1.0
load_force_z = -11772.0
load_x = 6.0
load_y = 0.0
load_z = 0.0

# Pre-calculate vertical positions
vertical_x_positions = [i * vertical_interval for i in range(int(span_x / vertical_interval) + 1)]
# Ensure last position is exactly span_x
vertical_x_positions[-1] = span_x

# ------------------------------------------------------------
# 3. Helper function to create a beam between two points
# ------------------------------------------------------------
def create_beam(point1, point2, cross_section, name, is_reinforced=False):
    """Create a rectangular beam as a cuboid between two points."""
    # Calculate direction and length
    vec = Vector(point2) - Vector(point1)
    length = vec.length
    if length == 0:
        return None
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length along local X, cross-section along Y and Z
    beam.scale = (length, cross_section, cross_section)
    
    # Position at midpoint
    mid = (Vector(point1) + Vector(point2)) / 2
    beam.location = mid
    
    # Rotate to align with direction vector
    # Default cube's local X axis points along world X; we rotate it to match 'vec'
    axis = vec.normalized()
    up = Vector((0, 0, 1))
    # Compute rotation using look_at method
    rot_quat = up.rotation_difference(axis)
    # But we need the cube's X axis to align with axis, not Z. So rotate 90° around Y.
    from mathutils import Euler
    rot_quat = rot_quat @ Euler((0, math.radians(90), 0)).to_quaternion()
    beam.rotation_mode = 'QUATERNION'
    beam.rotation_quaternion = rot_quat
    
    # Add rigid body (passive by default)
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = 10.0  # arbitrary mass for stability
    
    return beam

# ------------------------------------------------------------
# 4. Build the bridge
# ------------------------------------------------------------
beams = []  # store beam objects for later constraint creation
beam_endpoints = []  # store (beam, (p1, p2))

# Top chord (reinforced)
for y_sign in (-1, 1):
    y = y_sign * truss_y_offset
    p1 = (0.0, y, top_z)
    p2 = (span_x, y, top_z)
    beam = create_beam(p1, p2, reinforced_cross, f"TopChord_{y_sign}", is_reinforced=True)
    beams.append(beam)
    beam_endpoints.append((beam, (p1, p2)))

# Bottom chord (standard)
for y_sign in (-1, 1):
    y = y_sign * truss_y_offset
    p1 = (0.0, y, bottom_z)
    p2 = (span_x, y, bottom_z)
    beam = create_beam(p1, p2, standard_cross, f"BottomChord_{y_sign}")
    beams.append(beam)
    beam_endpoints.append((beam, (p1, p2)))

# Vertical members (standard)
for x in vertical_x_positions:
    for y_sign in (-1, 1):
        y = y_sign * truss_y_offset
        p1 = (x, y, bottom_z)
        p2 = (x, y, top_z)
        beam = create_beam(p1, p2, standard_cross, f"Vertical_{x}_{y_sign}")
        beams.append(beam)
        beam_endpoints.append((beam, (p1, p2)))

# Diagonal members (standard) - Pratt pattern
# Left half: diagonals from top at x to bottom at x+2
for i in range(len(vertical_x_positions) - 1):
    x1 = vertical_x_positions[i]
    x2 = vertical_x_positions[i + 1]
    for y_sign in (-1, 1):
        y = y_sign * truss_y_offset
        if x1 < span_x / 2:  # left half
            p1 = (x1, y, top_z)
            p2 = (x2, y, bottom_z)
        else:  # right half (including center)
            p1 = (x1, y, bottom_z)
            p2 = (x2, y, top_z)
        beam = create_beam(p1, p2, standard_cross, f"Diagonal_{x1}_{x2}_{y_sign}")
        beams.append(beam)
        beam_endpoints.append((beam, (p1, p2)))

# Central cross-beam to distribute load (standard)
cross_p1 = (load_x, -truss_y_offset, load_z)
cross_p2 = (load_x, truss_y_offset, load_z)
cross_beam = create_beam(cross_p1, cross_p2, standard_cross, "CrossBeam")
beams.append(cross_beam)
beam_endpoints.append((cross_beam, (cross_p1, cross_p2)))

# ------------------------------------------------------------
# 5. Create fixed constraints at joints (within tolerance)
# ------------------------------------------------------------
tolerance = 0.01
for i, (beam1, (p1a, p1b)) in enumerate(beam_endpoints):
    for j, (beam2, (p2a, p2b)) in enumerate(beam_endpoints):
        if i >= j:
            continue
        # Check if beams share a vertex
        points1 = [Vector(p1a), Vector(p1b)]
        points2 = [Vector(p2a), Vector(p2b)]
        for pt1 in points1:
            for pt2 in points2:
                if (pt1 - pt2).length < tolerance:
                    # Create fixed constraint
                    bpy.ops.rigidbody.constraint_add()
                    constraint = bpy.context.active_object
                    constraint.name = f"Fixed_{beam1.name}_{beam2.name}"
                    constraint.rigid_body_constraint.type = 'FIXED'
                    constraint.rigid_body_constraint.object1 = beam1
                    constraint.rigid_body_constraint.object2 = beam2
                    break

# ------------------------------------------------------------
# 6. Apply load to central cross-beam
# ------------------------------------------------------------
# Make cross-beam active rigid body to receive force
cross_beam.rigid_body.type = 'ACTIVE'
# Add constant force via rigid body settings
cross_beam.rigid_body.kinematic = False
cross_beam.rigid_body.use_deactivation = False
# Apply force directly (Blender doesn't have direct constant force property in bpy;
# we use a force field instead)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(load_x, load_y, load_z))
force_empty = bpy.context.active_object
force_empty.name = "ForceField"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = load_force_z
force_empty.field.use_max_distance = True
force_empty.field.distance_max = 1.0  # affect only nearby objects
# Link force field to cross-beam via a vertex group? Simpler: parent it to cross-beam.
force_empty.parent = cross_beam
force_empty.matrix_parent_inverse = cross_beam.matrix_world.inverted()

# ------------------------------------------------------------
# 7. Set up rigid body world
# ------------------------------------------------------------
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.use_split_impulse = True

print("Bridge construction complete. Ready for simulation.")