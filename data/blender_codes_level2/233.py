import bpy
import bmesh
from mathutils import Vector, Matrix
from math import sqrt, pi, cos, sin, acos, atan2
import itertools

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
R = 4.0
strut_a = 0.2
v_rad = 0.15
base_h = 0.4
base_w = 0.4
density = 7850.0
load_mass = 150.0
g = 9.81
freq = 2
break_thresh = 10000.0
base_z = 0.0
margin = 0.1

# Generate geodesic dome vertices
phi = (1 + sqrt(5)) / 2
ico_verts = [
    Vector((0, 1, phi)), Vector((0, -1, phi)), Vector((0, 1, -phi)), Vector((0, -1, -phi)),
    Vector((1, phi, 0)), Vector((-1, phi, 0)), Vector((1, -phi, 0)), Vector((-1, -phi, 0)),
    Vector((phi, 0, 1)), Vector((-phi, 0, 1)), Vector((phi, 0, -1)), Vector((-phi, 0, -1))
]
ico_verts = [v.normalized() * R for v in ico_verts]

ico_faces = [
    (0, 1, 8), (0, 8, 5), (0, 5, 10), (0, 10, 3), (0, 3, 9),
    (1, 0, 11), (1, 11, 6), (1, 6, 4), (1, 4, 8),
    (8, 4, 5), (5, 4, 10), (10, 4, 2), (10, 2, 3),
    (3, 2, 9), (9, 2, 7), (9, 7, 11), (11, 7, 6),
    (6, 7, 2), (6, 2, 4), (7, 2, 9)
]

# Subdivide triangles
vertices = ico_verts[:]
face_dict = {}
for f in ico_faces:
    face_dict[f] = True

for _ in range(freq):
    new_faces = {}
    new_vertices = vertices[:]
    vert_index = len(vertices)
    
    for (a, b, c) in list(face_dict.keys()):
        v1 = vertices[a]
        v2 = vertices[b]
        v3 = vertices[c]
        
        # Create midpoints
        m12 = (v1 + v2).normalized() * R
        m23 = (v2 + v3).normalized() * R
        m31 = (v3 + v1).normalized() * R
        
        # Add new vertices
        idx_m12 = vert_index
        new_vertices.append(m12)
        vert_index += 1
        
        idx_m23 = vert_index
        new_vertices.append(m23)
        vert_index += 1
        
        idx_m31 = vert_index
        new_vertices.append(m31)
        vert_index += 1
        
        # Create 4 new faces
        new_faces[(a, idx_m12, idx_m31)] = True
        new_faces[(idx_m12, b, idx_m23)] = True
        new_faces[(idx_m31, idx_m23, c)] = True
        new_faces[(idx_m12, idx_m23, idx_m31)] = True
    
    vertices = new_vertices
    face_dict = new_faces

# Extract edges from faces
edges = set()
for (a, b, c) in face_dict.keys():
    edges.add(tuple(sorted((a, b))))
    edges.add(tuple(sorted((b, c))))
    edges.add(tuple(sorted((c, a))))

# Create vertex connector objects
vertex_objects = []
for i, v in enumerate(vertices):
    if v.z > -R * cos(pi/6):  # Only create vertices above base cutoff
        bpy.ops.mesh.primitive_uv_sphere_add(radius=v_rad, location=v)
        vert_obj = bpy.context.active_object
        vert_obj.name = f"Vertex_{i}"
        bpy.ops.rigidbody.object_add()
        vert_obj.rigid_body.type = 'PASSIVE'
        vert_obj.rigid_body.collision_shape = 'SPHERE'
        vertex_objects.append((i, vert_obj))

# Create struts
strut_objects = []
edge_lengths = []
for (a, b) in edges:
    v1 = vertices[a]
    v2 = vertices[b]
    direction = (v2 - v1).normalized()
    length = (v2 - v1).length - 2 * margin
    
    if length > 0:  # Only create strut if positive length
        midpoint = v1 + direction * ((v2 - v1).length / 2)
        
        # Create cube and scale to strut dimensions
        bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
        strut = bpy.context.active_object
        strut.scale = Vector((length/2, strut_a/2, strut_a/2))
        
        # Rotate to align with edge direction
        up = Vector((0, 0, 1))
        rot_axis = up.cross(direction)
        rot_angle = up.angle(direction)
        if rot_axis.length > 0:
            strut.rotation_mode = 'AXIS_ANGLE'
            strut.rotation_axis_angle = (rot_angle, *rot_axis.normalized())
        
        strut.name = f"Strut_{a}_{b}"
        bpy.ops.rigidbody.object_add()
        strut.rigid_body.type = 'ACTIVE'
        strut.rigid_body.collision_shape = 'BOX'
        strut.rigid_body.mass = density * (length * strut_a * strut_a)
        
        strut_objects.append((a, b, strut))
        edge_lengths.append(length)

# Create base supports
base_vertices = [v for v in vertices if v.z <= -R * cos(pi/6) + 0.5]
for i, v in enumerate(base_vertices):
    base_pos = Vector((v.x, v.y, base_z))
    bpy.ops.mesh.primitive_cube_add(size=1, location=base_pos)
    base = bpy.context.active_object
    base.scale = Vector((base_w/2, base_w/2, base_h/2))
    base.name = f"Base_{i}"
    bpy.ops.rigidbody.object_add()
    base.rigid_body.type = 'PASSIVE'
    base.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between struts and vertices
for a, b, strut in strut_objects:
    # Find vertex objects
    vert_a_obj = next((obj for idx, obj in vertex_objects if idx == a), None)
    vert_b_obj = next((obj for idx, obj in vertex_objects if idx == b), None)
    
    if vert_a_obj:
        constraint = strut.constraints.new(type='RIGID_BODY_JOINT')
        constraint.object1 = strut
        constraint.object2 = vert_a_obj
        constraint.type = 'FIXED'
        constraint.use_breaking = True
        constraint.breaking_threshold = break_thresh
    
    if vert_b_obj:
        constraint = strut.constraints.new(type='RIGID_BODY_JOINT')
        constraint.object1 = strut
        constraint.object2 = vert_b_obj
        constraint.type = 'FIXED'
        constraint.use_breaking = True
        constraint.breaking_threshold = break_thresh

# Connect base supports to nearest vertices
for base in [obj for obj in bpy.data.objects if obj.name.startswith("Base_")]:
    base_pos = base.location
    nearest_vert = min(vertex_objects, 
                      key=lambda v: (v[1].location - base_pos).length)
    
    if nearest_vert:
        constraint = base.constraints.new(type='RIGID_BODY_JOINT')
        constraint.object1 = base
        constraint.object2 = nearest_vert[1]
        constraint.type = 'FIXED'
        constraint.use_breaking = True
        constraint.breaking_threshold = break_thresh * 2

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.gravity = Vector((0, 0, -g))

# Apply distributed load (additional mass to all struts)
total_strut_mass = sum(s[2].rigid_body.mass for s in strut_objects)
load_per_strut = load_mass * g / len(strut_objects)
for a, b, strut in strut_objects:
    # Add force to simulate distributed load
    strut.rigid_body.mass += load_mass / len(strut_objects)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print(f"Geodesic dome created with {len(strut_objects)} struts and {len(vertex_objects)} vertices")
print(f"Total structure mass: {sum(obj.rigid_body.mass for obj in bpy.data.objects if obj.rigid_body):.1f} kg")
print(f"Design load: {load_mass} kg ({load_mass * g:.1f} N)")