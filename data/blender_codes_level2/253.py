import bpy
import bmesh
from math import radians, sin, cos, pi, sqrt, ceil
from mathutils import Vector, Matrix

# ============================================================================
# CLEAR SCENE
# ============================================================================
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Clear existing collections
for collection in bpy.data.collections:
    if collection.name not in ['Master Collection']:
        bpy.data.collections.remove(collection)

# ============================================================================
# PARAMETERS FROM SUMMARY
# ============================================================================
# Dome
R = 8.0
BASE_VERTICES = 20
APEX_Z = 8.0
TRI_SIDE = 1.5

# Cube
CUBE_L = 0.5
CUBE_W = 0.5
CUBE_T = 0.05
CUBES_PER_EDGE = 3

# Load
LOAD_MASS = 600.0
LOAD_FORCE = 5886.0
LOAD_PLATE_X = 10.0
LOAD_PLATE_Y = 10.0
LOAD_PLATE_T = 0.1
LOAD_PLATE_Z = 7.45
LOAD_CLEARANCE = 0.5

# Simulation
SIM_FRAMES = 100
GRAVITY = -9.81

# Material
DENSITY = 7850.0

# ============================================================================
# GENERATE GEODESIC DOME VERTICES (Frequency-2)
# ============================================================================
def generate_geodesic_vertices(radius, base_count):
    """Generate vertices for frequency-2 geodesic dome"""
    vertices = []
    
    # Base vertices (circle at Z=0)
    for i in range(base_count):
        angle = radians(i * 360.0 / base_count)
        x = radius * cos(angle)
        y = radius * sin(angle)
        vertices.append(Vector((x, y, 0.0)))
    
    # Middle ring vertices (Z ≈ 4)
    middle_ring = 10
    for i in range(middle_ring):
        angle = radians(i * 360.0 / middle_ring)
        x = 0.8 * radius * cos(angle)
        y = 0.8 * radius * sin(angle)
        z = 0.6 * radius
        vertices.append(Vector((x, y, z)))
    
    # Upper ring vertices (Z ≈ 6.5)
    upper_ring = 5
    for i in range(upper_ring):
        angle = radians(i * 360.0 / upper_ring)
        x = 0.4 * radius * cos(angle)
        y = 0.4 * radius * sin(angle)
        z = 0.9 * radius
        vertices.append(Vector((x, y, z)))
    
    # Apex vertex
    vertices.append(Vector((0.0, 0.0, radius)))
    
    # Project all vertices to sphere surface
    for i, v in enumerate(vertices):
        if v.length > 0:
            vertices[i] = v.normalized() * radius
    
    return vertices

def generate_geodesic_faces(vertices):
    """Generate triangular faces for geodesic dome"""
    faces = []
    n = len(vertices)
    base_count = 20
    
    # Connect base ring (fan triangles to approximate circle)
    for i in range(base_count):
        next_i = (i + 1) % base_count
        # Create triangle from center of base circle to two base vertices
        center = Vector((0, 0, 0))
        if center not in vertices:
            vertices.append(center)
        center_idx = len(vertices) - 1
        faces.append((center_idx, i, next_i))
    
    # Connect middle ring to base
    middle_start = base_count
    middle_count = 10
    for i in range(middle_count):
        base_i1 = int(i * 2) % base_count
        base_i2 = (base_i1 + 1) % base_count
        middle_i = middle_start + i
        middle_next = middle_start + (i + 1) % middle_count
        
        # Create triangles
        faces.append((base_i1, middle_i, base_i2))
        faces.append((base_i1, middle_next, middle_i))
    
    # Connect upper ring to middle ring
    upper_start = base_count + middle_count
    upper_count = 5
    for i in range(upper_count):
        middle_i1 = middle_start + i * 2
        middle_i2 = middle_start + (i * 2 + 1) % middle_count
        upper_i = upper_start + i
        upper_next = upper_start + (i + 1) % upper_count
        
        # Create triangles
        faces.append((middle_i1, upper_i, middle_i2))
        faces.append((middle_i1, upper_next, upper_i))
    
    # Connect apex to upper ring
    apex_idx = len(vertices) - 1
    for i in range(upper_count):
        upper_i = upper_start + i
        upper_next = upper_start + (i + 1) % upper_count
        faces.append((apex_idx, upper_i, upper_next))
    
    return faces

# Generate vertices and faces
vertices = generate_geodesic_vertices(R, BASE_VERTICES)
faces = generate_geodesic_faces(vertices)

# ============================================================================
# CREATE CUBE NETWORK
# ============================================================================
# Collection for structure
structure_collection = bpy.data.collections.new("Dome_Structure")
bpy.context.scene.collection.children.link(structure_collection)

# Store cube objects for constraint creation
cube_objects = []
edge_cube_map = {}  # Maps (v1_idx, v2_idx) -> list of cube objects

def create_cube_between_points(p1, p2, edge_id):
    """Create cubes along edge between two points"""
    direction = (p2 - p1).normalized()
    edge_length = (p2 - p1).length
    segment_length = edge_length / CUBES_PER_EDGE
    
    cubes = []
    
    for i in range(CUBES_PER_EDGE):
        # Position cube at segment center
        t_start = i / CUBES_PER_EDGE
        t_end = (i + 1) / CUBES_PER_EDGE
        pos = p1.lerp(p2, (t_start + t_end) / 2.0)
        
        # Create cube
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
        cube = bpy.context.active_object
        cube.name = f"Cube_Edge{edge_id}_Seg{i}"
        
        # Scale to desired dimensions
        cube.scale = (segment_length, CUBE_W, CUBE_T)
        
        # Rotate to align with edge direction
        # Calculate rotation matrix
        z_up = Vector((0, 0, 1))
        rot_axis = direction.cross(z_up)
        rot_angle = direction.angle(z_up)
        
        if rot_axis.length > 0:
            cube.rotation_mode = 'AXIS_ANGLE'
            cube.rotation_axis_angle = (rot_angle, *rot_axis.normalized())
        
        # Move to structure collection
        if cube.name in bpy.data.objects:
            bpy.data.objects[cube.name].users_collection[0].objects.unlink(cube)
            structure_collection.objects.link(cube)
        
        cubes.append(cube)
    
    return cubes

# Create cubes for each triangular edge
for face in faces:
    v0_idx, v1_idx, v2_idx = face
    v0, v1, v2 = vertices[v0_idx], vertices[v1_idx], vertices[v2_idx]
    
    # Create edges (avoid duplicates)
    edges = [(v0_idx, v1_idx), (v1_idx, v2_idx), (v2_idx, v0_idx)]
    
    for v_idx1, v_idx2 in edges:
        edge_key = tuple(sorted((v_idx1, v_idx2)))
        
        if edge_key not in edge_cube_map:
            p1 = vertices[v_idx1]
            p2 = vertices[v_idx2]
            
            # Skip zero-length edges
            if (p1 - p2).length < 0.01:
                continue
            
            cubes = create_cube_between_points(p1, p2, f"{v_idx1}_{v_idx2}")
            edge_cube_map[edge_key] = cubes
            cube_objects.extend(cubes)

# ============================================================================
# ADD PHYSICS TO CUBES
# ============================================================================
for cube in cube_objects:
    bpy.context.view_layer.objects.active = cube
    bpy.ops.rigidbody.object_add()
    cube.rigid_body.type = 'ACTIVE'
    cube.rigid_body.mass = DENSITY * (CUBE_L * CUBE_W * CUBE_T)
    cube.rigid_body.collision_shape = 'BOX'
    cube.rigid_body.friction = 0.5
    cube.rigid_body.restitution = 0.1

# ============================================================================
# CREATE BASE ANCHORS
# ============================================================================
anchor_objects = []

for i in range(BASE_VERTICES):
    v = vertices[i]
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(v.x, v.y, 0.0))
    anchor = bpy.context.active_object
    anchor.name = f"Anchor_{i}"
    
    # Move to structure collection
    if anchor.name in bpy.data.objects:
        bpy.data.objects[anchor.name].users_collection[0].objects.unlink(anchor)
        structure_collection.objects.link(anchor)
    
    # Add physics (passive)
    bpy.ops.rigidbody.object_add()
    anchor.rigid_body.type = 'PASSIVE'
    anchor.rigid_body.collision_shape = 'BOX'
    
    anchor_objects.append(anchor)

# ============================================================================
# CREATE FIXED CONSTRAINTS
# ============================================================================
def add_fixed_constraint(obj_a, obj_b):
    """Add fixed constraint between two objects"""
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    
    # Move to structure collection
    if constraint.name in bpy.data.objects:
        bpy.data.objects[constraint.name].users_collection[0].objects.unlink(constraint)
        structure_collection.objects.link(constraint)
    
    return constraint

# Connect cubes along edges
for edge_key, cubes in edge_cube_map.items():
    for i in range(len(cubes) - 1):
        add_fixed_constraint(cubes[i], cubes[i + 1])

# Connect cubes at vertices (simplified: connect neighboring cubes)
for i in range(len(cube_objects) - 1):
    for j in range(i + 1, len(cube_objects)):
        # Only connect if cubes are close (simulating vertex connection)
        dist = (cube_objects[i].location - cube_objects[j].location).length
        if dist < CUBE_L * 1.5:
            add_fixed_constraint(cube_objects[i], cube_objects[j])

# Connect base cubes to anchors
for anchor_idx, anchor in enumerate(anchor_objects):
    anchor_pos = anchor.location
    
    # Find nearby cubes to connect
    for cube in cube_objects:
        dist = (cube.location - anchor_pos).length
        if dist < 1.5:  # Within connection range
            add_fixed_constraint(cube, anchor)

# ============================================================================
# CREATE LOAD PLATE
# ============================================================================
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, 0.0, LOAD_PLATE_Z)
)
load_plate = bpy.context.active_object
load_plate.name = "Load_Plate"
load_plate.scale = (LOAD_PLATE_X, LOAD_PLATE_Y, LOAD_PLATE_T)

# Move to structure collection
if load_plate.name in bpy.data.objects:
    bpy.data.objects[load_plate.name].users_collection[0].objects.unlink(load_plate)
structure_collection.objects.link(load_plate)

# Add physics
bpy.ops.rigidbody.object_add()
load_plate.rigid_body.type = 'ACTIVE'
load_plate.rigid_body.mass = LOAD_MASS
load_plate.rigid_body.collision_shape = 'BOX'
load_plate.rigid_body.friction = 0.5

# Connect load plate to upper dome cubes
upper_cubes = [cube for cube in cube_objects if cube.location.z > R * 0.5]
for cube in upper_cubes[:10]:  # Connect to first 10 upper cubes
    add_fixed_constraint(load_plate, cube)

# ============================================================================
# SETUP SCENE FOR SIMULATION
# ============================================================================
# Set gravity
bpy.context.scene.gravity = (0, 0, GRAVITY)

# Set rigid body world settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Set simulation end frame
bpy.context.scene.frame_end = SIM_FRAMES

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 0, -0.5))
ground = bpy.context.active_object
ground.name = "Ground"

# Add physics to ground
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

print(f"Geodesic dome created with {len(cube_objects)} cubes")
print(f"Load plate mass: {LOAD_MASS} kg")
print(f"Base anchors: {len(anchor_objects)}")
print(f"Ready for {SIM_FRAMES} frame simulation")