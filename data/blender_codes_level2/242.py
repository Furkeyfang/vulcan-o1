import bpy
import math
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
R = 6.0
BASE_Z = 6.0
BEAM_SECTION = 0.1
COL_RAD = 0.5
COL_H = 6.0
LOAD_MASS = 400.0
G = 9.81
FREQ = 2
HEMISPHERE = True

# Generate geodesic dome vertices (icosahedron subdivision)
def geodesic_dome_vertices(radius, frequency, hemisphere=True):
    # Icosahedron vertices (normalized)
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    verts = [
        (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
        (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
        (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)
    ]
    # Normalize to unit sphere
    verts = [mathutils.Vector(v).normalized() for v in verts]
    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
    ]
    
    # Subdivide triangles
    for _ in range(frequency):
        new_faces = []
        for face in faces:
            v0, v1, v2 = verts[face[0]], verts[face[1]], verts[face[2]]
            a = (v0 + v1).normalized()
            b = (v1 + v2).normalized()
            c = (v2 + v0).normalized()
            # Add new vertices
            idx_a = len(verts)
            verts.append(a)
            idx_b = len(verts)
            verts.append(b)
            idx_c = len(verts)
            verts.append(c)
            # Replace triangle with 4 smaller triangles
            new_faces.extend([
                (face[0], idx_a, idx_c),
                (face[1], idx_b, idx_a),
                (face[2], idx_c, idx_b),
                (idx_a, idx_b, idx_c)
            ])
        faces = new_faces
    
    # Scale and translate
    final_verts = []
    for v in verts:
        if hemisphere and v.z < 0:
            continue
        scaled = v * radius
        scaled.z += BASE_Z
        final_verts.append(scaled)
    
    # Deduplicate (floating point tolerance)
    unique_verts = []
    for v in final_verts:
        if not any((v - uv).length < 1e-4 for uv in unique_verts):
            unique_verts.append(v)
    
    return unique_verts

# Generate edges from proximity (distance < radius * 1.5)
def generate_edges(vertices, max_dist_factor=1.5):
    edges = []
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            dist = (vertices[i] - vertices[j]).length
            if dist < R * max_dist_factor:
                edges.append((i, j))
    return edges

# Create beam between two points
def create_beam(v1, v2, name):
    vec = v2 - v1
    length = vec.length
    mid = (v1 + v2) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (BEAM_SECTION, BEAM_SECTION, length)
    beam.location = mid
    # Rotate to align with edge vector
    beam.rotation_mode = 'QUATERNION'
    beam.rotation_quaternion = mathutils.Vector((0, 0, 1)).rotation_difference(vec)
    
    # Rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.collision_margin = 0.0
    return beam

# Create vertices and edges
vertices = geodesic_dome_vertices(R, FREQ, HEMISPHERE)
edges = generate_edges(vertices, max_dist_factor=1.2)

# Create central column
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=COL_RAD, depth=COL_H)
column = bpy.context.active_object
column.name = "CentralColumn"
column.location = (0, 0, COL_H / 2)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'CYLINDER'
column.rigid_body.collision_margin = 0.0

# Create beams
beams = []
for idx, (i, j) in enumerate(edges):
    beam = create_beam(vertices[i], vertices[j], f"Beam_{idx:03d}")
    beams.append(beam)

# Create Fixed Constraints between beams at shared vertices
# We'll create empty objects at vertices and parent constraints to them
vertex_empties = []
for v_idx, v_pos in enumerate(vertices):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=v_pos)
    empty = bpy.context.active_object
    empty.name = f"Vertex_{v_idx:03d}"
    empty.hide_viewport = True
    empty.hide_render = True
    vertex_empties.append(empty)
    
    # Find all beams that contain this vertex
    connected_beams = []
    for beam in beams:
        beam_vec = beam.matrix_world @ mathutils.Vector((0, 0, -0.5 * beam.scale.z))
        beam_vec2 = beam.matrix_world @ mathutils.Vector((0, 0, 0.5 * beam.scale.z))
        if (beam_vec - v_pos).length < 0.1 or (beam_vec2 - v_pos).length < 0.1:
            connected_beams.append(beam)
    
    # Create fixed constraints between all connected beams at this vertex
    if len(connected_beams) > 1:
        for k in range(len(connected_beams)-1):
            bpy.ops.rigidbody.constraint_add()
            const = bpy.context.active_object
            const.name = f"Fixed_{v_idx:03d}_{k}"
            const.rigid_body_constraint.type = 'FIXED'
            const.rigid_body_constraint.object1 = connected_beams[0]
            const.rigid_body_constraint.object2 = connected_beams[k+1]
            const.location = v_pos

# Attach base vertices to column top (Z = BASE_Z)
base_vertices = [v for v in vertices if abs(v.z - BASE_Z) < 0.1]
for idx, v_pos in enumerate(base_vertices):
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.name = f"BaseAnchor_{idx:03d}"
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = column
    # Find a beam attached to this base vertex
    for beam in beams:
        beam_vec = beam.matrix_world @ mathutils.Vector((0, 0, -0.5 * beam.scale.z))
        beam_vec2 = beam.matrix_world @ mathutils.Vector((0, 0, 0.5 * beam.scale.z))
        if (beam_vec - v_pos).length < 0.1 or (beam_vec2 - v_pos).length < 0.1:
            const.rigid_body_constraint.object2 = beam
            break
    const.location = v_pos

# Apply load: downward force on each vertex (distributed mass)
force_per_vertex = LOAD_MASS * G / len(vertices)
for v_idx, v_pos in enumerate(vertices):
    # Create force field (downward)
    bpy.ops.object.effector_add(type='FORCE', location=v_pos)
    force = bpy.context.active_object
    force.name = f"Load_{v_idx:03d}"
    force.field.strength = -force_per_vertex
    force.field.direction = 'Z'
    force.field.falloff_power = 0
    force.field.use_max_distance = True
    force.field.max_distance = 0.5  # Only affect nearby objects

# Setup rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100

print(f"Created dome with {len(vertices)} vertices and {len(edges)} beams")
print(f"Load: {LOAD_MASS} kg = {LOAD_MASS * G} N")
print(f"Force per vertex: {force_per_vertex:.2f} N")