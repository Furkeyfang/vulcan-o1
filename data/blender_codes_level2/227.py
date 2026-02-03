import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters (from summary)
canopy_width = 12.0
canopy_length = 12.0
frame_elevation = 4.0
primary_beam_cross_section = (0.3, 0.3)
primary_beam_length = 12.0
secondary_beam_cross_section = (0.2, 0.2)
diagonal_length = 5.65685
column_radius = 0.25
column_height = 4.0
grid_spacing = 4.0
y_positions_primary = [-6.0, -2.0, 2.0, 6.0]
x_positions_primary = [-6.0, -2.0, 2.0, 6.0]
load_plate_dim = (12.0, 12.0, 0.1)
load_plate_mass_kg = 3000.0
load_plate_z = 4.25
steel_density = 7850.0

# Helper to create a beam with physics
def create_beam(name, loc, rot, scale, mass=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = scale
    beam.rotation_euler = rot
    bpy.ops.rigidbody.object_add()
    if mass is None:
        # Calculate mass from volume and steel density
        volume = scale[0] * scale[1] * scale[2]
        mass = volume * steel_density
    beam.rigid_body.mass = mass
    return beam

# Create primary beams (longitudinal, X-axis)
primary_beams = []
for i, y in enumerate(y_positions_primary):
    scale = (primary_beam_length, primary_beam_cross_section[0], primary_beam_cross_section[1])
    loc = (0.0, y, frame_elevation)
    rot = (0.0, 0.0, 0.0)
    beam = create_beam(f"Primary_X_{i}", loc, rot, scale)
    primary_beams.append(beam)

# Create primary beams (transverse, Y-axis)
for i, x in enumerate(x_positions_primary):
    scale = (primary_beam_cross_section[0], primary_beam_length, primary_beam_cross_section[1])
    loc = (x, 0.0, frame_elevation)
    rot = (0.0, 0.0, 0.0)
    beam = create_beam(f"Primary_Y_{i}", loc, rot, scale)
    primary_beams.append(beam)

# Create diagonal bracing beams in each grid cell
secondary_beams = []
cell_offsets = [(-grid_spacing/2, -grid_spacing/2), (-grid_spacing/2, grid_spacing/2),
                (grid_spacing/2, -grid_spacing/2), (grid_spacing/2, grid_spacing/2)]
for x_base in [-6.0, -2.0, 2.0]:
    for y_base in [-6.0, -2.0, 2.0]:
        # Diagonal 1: from (x_base, y_base) to (x_base+4, y_base+4)
        start = (x_base, y_base, frame_elevation)
        end = (x_base + grid_spacing, y_base + grid_spacing, frame_elevation)
        mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, start[2])
        length = math.hypot(grid_spacing, grid_spacing)
        angle = math.atan2(end[1]-start[1], end[0]-start[0])
        scale = (length, secondary_beam_cross_section[0], secondary_beam_cross_section[1])
        rot = (0.0, 0.0, angle)
        beam = create_beam(f"Diagonal_{x_base}_{y_base}_1", mid, rot, scale)
        secondary_beams.append(beam)
        
        # Diagonal 2: from (x_base+4, y_base) to (x_base, y_base+4)
        start = (x_base + grid_spacing, y_base, frame_elevation)
        end = (x_base, y_base + grid_spacing, frame_elevation)
        mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, start[2])
        angle = math.atan2(end[1]-start[1], end[0]-start[0])
        beam = create_beam(f"Diagonal_{x_base}_{y_base}_2", mid, rot, scale)
        secondary_beams.append(beam)

# Create support columns (passive rigid bodies)
columns = []
corner_positions = [(-6.0, -6.0), (-6.0, 6.0), (6.0, -6.0), (6.0, 6.0)]
for i, (x, y) in enumerate(corner_positions):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=column_radius, depth=column_height, location=(x, y, column_height/2))
    col = bpy.context.active_object
    col.name = f"Column_{i}"
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    columns.append(col)

# Create fixed constraints between intersecting beams and columns
all_beams = primary_beams + secondary_beams
# Group objects by their intersection points (rounded to 0.01 m tolerance)
from collections import defaultdict
intersection_map = defaultdict(list)
for obj in all_beams + columns:
    # For beams, use their center (since they are centered at intersection for diagonals)
    # For columns, use their top center (at frame elevation)
    if "Column" in obj.name:
        point = (round(obj.location.x, 2), round(obj.location.y, 2), round(frame_elevation, 2))
    else:
        point = (round(obj.location.x, 2), round(obj.location.y, 2), round(obj.location.z, 2))
    intersection_map[point].append(obj)

# Create fixed constraints between objects sharing an intersection point
for point, objects in intersection_map.items():
    if len(objects) < 2:
        continue
    parent = objects[0]
    for child in objects[1:]:
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.name = f"Fixed_{parent.name}_{child.name}"
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = parent
        constraint.rigid_body_constraint.object2 = child
        constraint.location = point

# Create load plate
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, 0.0, load_plate_z))
plate = bpy.context.active_object
plate.name = "Load_Plate"
plate.scale = load_plate_dim
bpy.ops.rigidbody.object_add()
plate.rigid_body.mass = load_plate_mass_kg
plate.rigid_body.collision_shape = 'BOX'

# Set world gravity for realistic load simulation
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Ensure all rigid bodies have proper collision margins
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.0