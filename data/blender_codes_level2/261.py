import bpy
import math
from mathutils import Vector, Quaternion

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
R = 5.5
strut_w = 0.1
strut_h = 0.1
base_tol = 0.1
total_load = 2943.0
vertex_mass = 1.0
strut_density = 100.0
sim_frames = 100
ground_size = 15.0
phi = (1 + math.sqrt(5)) / 2
norm = math.sqrt(1 + phi**2)

# Generate icosahedron vertices (12 points)
verts_normalized = [
    (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
    (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
    (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, 1)
]
verts_normalized = [Vector(v) / norm for v in verts_normalized]

# Icosahedron faces (20 triangles)
faces = [
    (0, 4, 1), (0, 9, 4), (9, 5, 4), (4, 5, 8), (4, 8, 0),
    (0, 8, 3), (0, 3, 9), (9, 3, 2), (9, 2, 5), (5, 2, 7),
    (5, 7, 8), (8, 7, 3), (3, 7, 2), (1, 6, 0), (0, 6, 11),
    (11, 6, 10), (11, 10, 1), (1, 10, 6), (1, 4, 11), (11, 4, 9)
]

# 2V tessellation: subdivide each face into 4 triangles
subdivided_verts = []
subdivided_faces = []
vert_map = {}  # Cache for edge midpoints

def get_midpoint(v1_idx, v2_idx):
    """Get or create midpoint vertex index"""
    key = tuple(sorted((v1_idx, v2_idx)))
    if key in vert_map:
        return vert_map[key]
    
    p1 = verts_normalized[v1_idx]
    p2 = verts_normalized[v2_idx]
    mid = (p1 + p2).normalized()
    new_idx = len(verts_normalized) + len(subdivided_verts)
    subdivided_verts.append(mid)
    vert_map[key] = new_idx
    return new_idx

# Generate subdivided faces
for face in faces:
    a, b, c = face
    ab = get_midpoint(a, b)
    bc = get_midpoint(b, c)
    ca = get_midpoint(c, a)
    
    subdivided_faces.extend([
        (a, ab, ca),
        (b, bc, ab),
        (c, ca, bc),
        (ab, bc, ca)
    ])

# Combine all vertices and scale by radius
all_verts = verts_normalized + subdivided_verts
all_verts = [v * R for v in all_verts]

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create vertex empties and track base vertices
vertex_objects = []
base_vertices = []

for i, vert in enumerate(all_verts):
    bpy.ops.object.empty_add(type='SPHERE', location=vert)
    empty = bpy.context.active_object
    empty.name = f"Vertex_{i}"
    empty.scale = (0.3, 0.3, 0.3)
    bpy.ops.rigidbody.object_add()
    
    # Base vertices (Z near 0) are passive anchors
    if vert.z <= base_tol:
        empty.rigid_body.type = 'PASSIVE'
        base_vertices.append(empty)
    else:
        empty.rigid_body.type = 'ACTIVE'
        empty.rigid_body.mass = vertex_mass
    
    vertex_objects.append(empty)

# Create struts for all edges in subdivided faces
strut_objects = []
edges_set = set()

for face in subdivided_faces:
    for i in range(3):
        v1_idx, v2_idx = face[i], face[(i + 1) % 3]
        edge = tuple(sorted((v1_idx, v2_idx)))
        if edge in edges_set:
            continue
        edges_set.add(edge)
        
        v1 = all_verts[v1_idx]
        v2 = all_verts[v2_idx]
        direction = v2 - v1
        length = direction.length
        midpoint = (v1 + v2) / 2
        
        # Create strut as rotated cube
        bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
        strut = bpy.context.active_object
        strut.name = f"Strut_{v1_idx}_{v2_idx}"
        strut.scale = (strut_w, strut_h, length / 2)  # Cube default size 2, so divide by 2
        
        # Rotate to align with edge direction
        if length > 0.001:
            rot_quat = direction.to_track_quat('Z', 'Y')
            strut.rotation_euler = rot_quat.to_euler()
        
        # Add rigid body with calculated mass
        bpy.ops.rigidbody.object_add()
        strut.rigid_body.type = 'ACTIVE'
        strut.rigid_body.mass = length * strut_w * strut_h * strut_density
        
        strut_objects.append((strut, v1_idx, v2_idx))

# Create fixed constraints between struts and vertices
for strut, v1_idx, v2_idx in strut_objects:
    # Constraint to first vertex
    bpy.ops.object.empty_add(type='ARROWS', location=vertex_objects[v1_idx].location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{strut.name}_to_{v1_idx}"
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = strut
    constraint.object2 = vertex_objects[v1_idx]
    
    # Constraint to second vertex  
    bpy.ops.object.empty_add(type='ARROWS', location=vertex_objects[v2_idx].location)
    constraint_empty2 = bpy.context.active_object
    constraint_empty2.name = f"Constraint_{strut.name}_to_{v2_idx}"
    bpy.ops.rigidbody.constraint_add()
    constraint2 = constraint_empty2.rigid_body_constraint
    constraint2.type = 'FIXED'
    constraint2.object1 = strut
    constraint2.object2 = vertex_objects[v2_idx]

# Apply distributed load to vertices (proportional to Z coordinate)
total_z = sum(max(v.z, 0) for v in all_verts)  # Only positive Z contributes
for i, (vert_obj, vert_pos) in enumerate(zip(vertex_objects, all_verts)):
    if vert_obj.rigid_body.type == 'ACTIVE':
        # Load proportional to vertical position
        load_fraction = max(vert_pos.z, 0) / total_z if total_z > 0 else 0
        force_z = -total_load * load_fraction  # Negative Z = downward
        
        # Apply as initial force (Blender applies this over time)
        vert_obj.rigid_body.force = (0, 0, force_z)

# Set up rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

print(f"Geodesic dome constructed with {len(vertex_objects)} vertices, {len(strut_objects)} struts")
print(f"Base anchored at {len(base_vertices)} vertices")
print(f"Total load: {total_load}N distributed across vertices")