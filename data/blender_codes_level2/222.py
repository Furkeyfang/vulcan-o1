import bpy
import math
import mathutils
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
R = 7.0
cross_section = 0.15
load_mass = 500.0
load_height_offset = 0.2
freq = 2
collision_margin = 0.001
linear_damping = 0.04
angular_damping = 0.1
bottom_threshold = 0.01

# Generate geodesic sphere vertices (icosahedron-based)
def geodesic_sphere_vertices(freq, radius):
    # Icosahedron vertices (golden ratio)
    t = (1.0 + math.sqrt(5.0)) / 2.0
    verts = [
        (-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
        (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
        (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)
    ]
    verts = [Vector(v) for v in verts]
    
    # Icosahedron faces (20 triangles)
    faces = [
        (0,11,5), (0,5,1), (0,1,7), (0,7,10), (0,10,11),
        (1,5,9), (5,11,4), (11,10,2), (10,7,6), (7,1,8),
        (3,9,4), (3,4,2), (3,2,6), (3,6,8), (3,8,9),
        (4,9,5), (2,4,11), (6,2,10), (8,6,7), (9,8,1)
    ]
    
    # Subdivide triangles
    edges = {}
    def get_midpoint(i, j):
        key = tuple(sorted((i, j)))
        if key not in edges:
            v1 = verts[i]
            v2 = verts[j]
            edges[key] = len(verts)
            verts.append((v1 + v2).normalized())
        return edges[key]
    
    for _ in range(freq):
        new_faces = []
        for a, b, c in faces:
            ab = get_midpoint(a, b)
            bc = get_midpoint(b, c)
            ca = get_midpoint(c, a)
            new_faces.extend([
                (a, ab, ca),
                (b, bc, ab),
                (c, ca, bc),
                (ab, bc, ca)
            ])
        faces = new_faces
    
    # Project to sphere and filter hemisphere (Z >= 0)
    sphere_verts = []
    for v in verts:
        v_normalized = v.normalized()
        if v_normalized.z >= 0:
            sphere_verts.append(v_normalized * R)
    
    return sphere_verts, faces

# Create cube along edge
def create_beam(v1, v2, cross_size, name):
    # Calculate edge properties
    midpoint = (v1 + v2) * 0.5
    direction = (v2 - v1).normalized()
    length = (v2 - v1).length
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=midpoint)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length along X, cross-section along Y and Z
    beam.scale = (length/2, cross_size/2, cross_size/2)
    
    # Rotate to align with edge
    up = Vector((0, 0, 1))
    if direction.dot(up) > 0.99:
        rot_axis = Vector((1, 0, 0))
    else:
        rot_axis = direction.cross(up).normalized()
    angle = direction.angle(up)
    beam.rotation_mode = 'AXIS_ANGLE'
    beam.rotation_axis_angle = (angle, *rot_axis)
    
    return beam

# Main construction
verts, faces = geodesic_sphere_vertices(freq, R)

# Extract unique edges from faces
edges_set = set()
for f in faces:
    a, b, c = f
    edges_set.add(tuple(sorted((a, b))))
    edges_set.add(tuple(sorted((b, c))))
    edges_set.add(tuple(sorted((c, a))))

# Filter edges where both vertices are in hemisphere
valid_edges = []
for i, j in edges_set:
    if i < len(verts) and j < len(verts):
        valid_edges.append((i, j))

# Create beam cubes
beams = []
for idx, (i, j) in enumerate(valid_edges):
    beam = create_beam(verts[i], verts[j], cross_section, f"Beam_{idx:03d}")
    beams.append(beam)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.collision_margin = collision_margin
    beam.rigid_body.linear_damping = linear_damping
    beam.rigid_body.angular_damping = angular_damping
    
    # Set bottom beams as passive (anchored)
    if verts[i].z <= bottom_threshold or verts[j].z <= bottom_threshold:
        beam.rigid_body.type = 'PASSIVE'

# Create fixed constraints between beams sharing vertices
vertex_to_beams = {}
for idx, (i, j) in enumerate(valid_edges):
    vertex_to_beams.setdefault(i, []).append(beams[idx])
    vertex_to_beams.setdefault(j, []).append(beams[idx])

for vertex_idx, beam_list in vertex_to_beams.items():
    if len(beam_list) > 1:
        # Create constraints between first beam and others
        base_beam = beam_list[0]
        for other_beam in beam_list[1:]:
            # Create constraint at vertex location
            constraint_loc = verts[vertex_idx]
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_loc)
            constraint = bpy.context.active_object
            constraint.name = f"Constraint_v{vertex_idx:03d}"
            
            bpy.ops.rigidbody.constraint_add()
            constraint.rigid_body_constraint.type = 'FIXED'
            constraint.rigid_body_constraint.object1 = base_beam
            constraint.rigid_body_constraint.object2 = other_beam

# Create load cube at apex
apex = Vector((0, 0, R + load_height_offset))
bpy.ops.mesh.primitive_cube_add(size=0.5, location=apex)
load_cube = bpy.context.active_object
load_cube.name = "Load_500kg"

# Add rigid body with mass
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.mass = load_mass
load_cube.rigid_body.collision_margin = collision_margin

# Set up rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

print(f"Geodesic dome constructed with {len(beams)} beams")
print(f"Load: {load_mass}kg at apex")