import bpy
import math
from math import cos, sin, radians, sqrt

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# ========== PARAMETERS (from summary) ==========
hex_diameter = 8.0
hex_radius = 4.0
column_height = 3.0
column_section = 0.2
beam_section = 0.15
node_size = 0.2
roof_base_z = 3.0
roof_top_z = 3.15
total_load_kg = 1000.0
collision_margin = 0.04

# Derived
column_center_z = column_height / 2.0
vertex_angles = [0, 60, 120, 180, 240, 300]
vertex_positions = [(hex_radius * cos(radians(a)), hex_radius * sin(radians(a)), 0.0) for a in vertex_angles]
center_pos = (0.0, 0.0, roof_top_z)

# ========== HELPER FUNCTIONS ==========
def create_cube(name, location, scale, rigid_body_type='ACTIVE', mass=1.0, collision_margin=0.04):
    """Create a cube with rigid body properties."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_margin = collision_margin
    return obj

def create_beam(name, start, end, section):
    """Create a beam as a cube oriented from start to end."""
    # Calculate midpoint, length, and direction
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2)
    length = sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2 + (end[2]-start[2])**2)
    if length < 0.001:
        return None
    
    # Create cube at origin, then transform
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: default cube is 2 units wide, so section/2 and length/2
    beam.scale = (section/2, section/2, length/2)
    
    # Align local Z to direction vector
    direction = (end[0]-start[0], end[1]-start[1], end[2]-start[2])
    direction_norm = (direction[0]/length, direction[1]/length, direction[2]/length)
    
    # Use rotation difference between global Z (0,0,1) and direction
    axis = (0, 0, 1)
    if abs(direction_norm[2]) < 0.999:
        # Calculate rotation using Euler (simplified)
        beam.rotation_euler = (0, 0, 0)  # Reset
        # Use track-to constraint method via Python (headless compatible)
        from mathutils import Vector, Matrix
        vec = Vector(direction_norm)
        up = Vector((0, 1, 0))
        if vec.dot(up) > 0.99:
            up = Vector((1, 0, 0))
        rot = vec.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
        beam.matrix_world = Matrix.Translation(mid) @ rot @ Matrix.Scale(1, 4, (1,1,1))
    else:
        beam.location = mid
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_margin = collision_margin
    return beam

def add_fixed_constraint(obj_a, obj_b):
    """Add a fixed constraint between two objects."""
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# ========== CREATE COLUMNS ==========
columns = []
for i, vpos in enumerate(vertex_positions):
    col_name = f"Column_{i}"
    col_loc = (vpos[0], vpos[1], column_center_z)
    col_scale = (column_section, column_section, column_height)
    col = create_cube(col_name, col_loc, col_scale, 'PASSIVE', 0.0, collision_margin)
    columns.append(col)

# ========== CREATE ROOF NODES ==========
# Nodes at vertices (top of columns)
vertex_nodes = []
for i, vpos in enumerate(vertex_positions):
    node_name = f"Node_Vertex_{i}"
    node_loc = (vpos[0], vpos[1], roof_top_z)
    node_scale = (node_size, node_size, node_size)
    node = create_cube(node_name, node_loc, node_scale, 'ACTIVE', 1.0, collision_margin)
    vertex_nodes.append(node)

# Central node
center_node = create_cube("Node_Center", center_pos, (node_size, node_size, node_size), 'ACTIVE', 1.0, collision_margin)

# ========== CREATE ROOF BEAMS ==========
beams = []
# Radial beams: center to each vertex
for i, node in enumerate(vertex_nodes):
    beam_name = f"Beam_Radial_{i}"
    beam = create_beam(beam_name, center_pos, node.location, beam_section)
    if beam:
        beams.append(beam)

# Perimeter beams: connect adjacent vertices
for i in range(len(vertex_nodes)):
    j = (i + 1) % len(vertex_nodes)
    beam_name = f"Beam_Perimeter_{i}_{j}"
    beam = create_beam(beam_name, vertex_nodes[i].location, vertex_nodes[j].location, beam_section)
    if beam:
        beams.append(beam)

# Optional diagonal beams for triangular grid (vertex to next-but-one vertex)
for i in range(len(vertex_nodes)):
    j = (i + 2) % len(vertex_nodes)
    beam_name = f"Beam_Diagonal_{i}_{j}"
    beam = create_beam(beam_name, vertex_nodes[i].location, vertex_nodes[j].location, beam_section)
    if beam:
        beams.append(beam)

# ========== DISTRIBUTE LOAD ==========
# Calculate total volume of roof members
node_volume = node_size ** 3
beam_volume_total = 0.0
for beam in beams:
    # Beam volume = section^2 * length (scale.z is length/2, default cube size 2)
    length = beam.scale.z * 2  # because we scaled by length/2
    beam_volume = beam_section ** 2 * length
    beam_volume_total += beam_volume

total_nodes = len(vertex_nodes) + 1  # vertices + center
total_roof_volume = (total_nodes * node_volume) + beam_volume_total
if total_roof_volume > 0:
    density = total_load_kg / total_roof_volume
else:
    density = 1.0

# Assign masses
for node in vertex_nodes + [center_node]:
    node.rigid_body.mass = density * node_volume
for beam in beams:
    length = beam.scale.z * 2
    beam_vol = beam_section ** 2 * length
    beam.rigid_body.mass = density * beam_vol

# ========== ADD CONSTRAINTS ==========
# Column to vertex node (fixed)
for col, node in zip(columns, vertex_nodes):
    add_fixed_constraint(col, node)

# Radial beams to center node and vertex nodes
for i, beam in enumerate(beams):
    if "Radial" in beam.name:
        add_fixed_constraint(beam, center_node)
        add_fixed_constraint(beam, vertex_nodes[i])

# Perimeter beams to two vertex nodes (simplified: connect to both vertices)
for beam in beams:
    if "Perimeter" in beam.name:
        # Parse indices from name
        parts = beam.name.split('_')
        idx1 = int(parts[-2])
        idx2 = int(parts[-1])
        add_fixed_constraint(beam, vertex_nodes[idx1])
        add_fixed_constraint(beam, vertex_nodes[idx2])

# Diagonal beams similarly
for beam in beams:
    if "Diagonal" in beam.name:
        parts = beam.name.split('_')
        idx1 = int(parts[-2])
        idx2 = int(parts[-1])
        add_fixed_constraint(beam, vertex_nodes[idx1])
        add_fixed_constraint(beam, vertex_nodes[idx2])

# ========== SCENE SETUP ==========
# Set gravity
bpy.context.scene.gravity = (0, 0, -9.81)
# Set rigid body world settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
# Set simulation end frame
bpy.context.scene.frame_end = 500

print(f"Structure built. Total roof mass: {sum(obj.rigid_body.mass for obj in vertex_nodes + [center_node] + beams):.2f} kg")