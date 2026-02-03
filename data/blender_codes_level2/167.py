import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ====================
# PARAMETERS (from summary)
# ====================
# Mast
MAST_H = 28.0
BASE_SIDE = 2.0
VERT_CROSS = 0.5
HORIZ_CROSS = 0.3
BRACE_INT = 4.0
NUM_LEVELS = 6

# Platform
PLATFORM_SIZE = (2.0, 2.0, 0.5)
PLATFORM_MASS = 300.0

# Precomputed geometry
TRI_HEIGHT = math.sqrt(3)  # ~1.732
CENTROID_Y = TRI_HEIGHT / 3  # ~0.577
DIAG_LEN = math.sqrt(BASE_SIDE**2 + BRACE_INT**2)  # ~4.472

# Base vertices
V1 = Vector((0.0, 0.0, 0.0))
V2 = Vector((BASE_SIDE, 0.0, 0.0))
V3 = Vector((BASE_SIDE/2, TRI_HEIGHT, 0.0))
vertices = [V1, V2, V3]

# Bracing levels
levels = [BRACE_INT * (i+1) for i in range(NUM_LEVELS)]  # [4,8,12,16,20,24]

# Platform center
platform_center = Vector((BASE_SIDE/2, CENTROID_Y, MAST_H + PLATFORM_SIZE[2]/2))

# ====================
# HELPER FUNCTIONS
# ====================
def create_beam(name, location, scale, rotation=None):
    """Create a cube beam with given transform"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = scale
    
    if rotation:
        beam.rotation_euler = rotation
    
    # Add rigid body (passive by default)
    bpy.ops.rigidbody.object_add()
    return beam

def add_fixed_constraint(obj_a, obj_b):
    """Create a fixed constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_a.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# ====================
# CREATE VERTICAL BEAMS
# ====================
vertical_beams = []
for i, vertex in enumerate(vertices):
    # Center of beam is at midpoint in Z
    beam_center = Vector((vertex.x, vertex.y, MAST_H/2))
    beam = create_beam(
        name=f"Vertical_Beam_{i+1}",
        location=beam_center,
        scale=(VERT_CROSS, VERT_CROSS, MAST_H)
    )
    vertical_beams.append(beam)

# ====================
# CREATE BRACING
# ====================
# Define triangle edges (vertex pairs)
edges = [(0,1), (1,2), (2,0)]

for level_z in levels:
    # ----------
    # HORIZONTAL BRACING
    # ----------
    for edge_idx, (v1_idx, v2_idx) in enumerate(edges):
        # Get the two vertices
        p1 = vertices[v1_idx]
        p2 = vertices[v2_idx]
        
        # Midpoint at this Z level
        mid = Vector(((p1.x + p2.x)/2, (p1.y + p2.y)/2, level_z))
        
        # Direction vector and length
        dir_vec = p2 - p1
        length = dir_vec.length
        
        # Rotation: align beam along edge
        # Default cube is aligned with world, need to rotate around Z
        angle = math.atan2(dir_vec.y, dir_vec.x)
        
        beam = create_beam(
            name=f"Horizontal_Level{level_z}_Edge{edge_idx}",
            location=mid,
            scale=(HORIZ_CROSS, HORIZ_CROSS, length),
            rotation=(0, 0, angle)
        )
        
        # Add constraints to both vertical beams
        add_fixed_constraint(beam, vertical_beams[v1_idx])
        add_fixed_constraint(beam, vertical_beams[v2_idx])
    
    # ----------
    # DIAGONAL BRACING (X-pattern on each face)
    # ----------
    if level_z > levels[0]:  # Need previous level for diagonals
        prev_z = level_z - BRACE_INT
        
        for edge_idx, (v1_idx, v2_idx) in enumerate(edges):
            # Create two diagonals per face: bottom-left to top-right and bottom-right to top-left
            
            # Diagonal 1: from (v1, prev_z) to (v2, level_z)
            start1 = Vector((vertices[v1_idx].x, vertices[v1_idx].y, prev_z))
            end1 = Vector((vertices[v2_idx].x, vertices[v2_idx].y, level_z))
            mid1 = (start1 + end1) / 2
            
            # Vector and orientation
            vec1 = end1 - start1
            length1 = vec1.length
            
            # Calculate rotation: align with 3D vector
            # Use Euler angles from direction vector
            rot_quat = vec1.to_track_quat('Z', 'Y')
            
            beam1 = create_beam(
                name=f"Diagonal1_Level{level_z}_Face{edge_idx}",
                location=mid1,
                scale=(HORIZ_CROSS, HORIZ_CROSS, length1)
            )
            beam1.rotation_euler = rot_quat.to_euler()
            
            # Add constraints
            add_fixed_constraint(beam1, vertical_beams[v1_idx])
            add_fixed_constraint(beam1, vertical_beams[v2_idx])
            
            # Diagonal 2: from (v2, prev_z) to (v1, level_z)
            start2 = Vector((vertices[v2_idx].x, vertices[v2_idx].y, prev_z))
            end2 = Vector((vertices[v1_idx].x, vertices[v1_idx].y, level_z))
            mid2 = (start2 + end2) / 2
            
            vec2 = end2 - start2
            length2 = vec2.length
            rot_quat2 = vec2.to_track_quat('Z', 'Y')
            
            beam2 = create_beam(
                name=f"Diagonal2_Level{level_z}_Face{edge_idx}",
                location=mid2,
                scale=(HORIZ_CROSS, HORIZ_CROSS, length2)
            )
            beam2.rotation_euler = rot_quat2.to_euler()
            
            # Add constraints
            add_fixed_constraint(beam2, vertical_beams[v1_idx])
            add_fixed_constraint(beam2, vertical_beams[v2_idx])

# ====================
# CREATE TOP PLATFORM
# ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_center)
platform = bpy.context.active_object
platform.name = "Top_Platform"
platform.scale = PLATFORM_SIZE

# Add rigid body with mass
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.mass = PLATFORM_MASS

# Fix platform to all three vertical beams
for v_beam in vertical_beams:
    add_fixed_constraint(platform, v_beam)

# ====================
# SET UP PHYSICS WORLD
# ====================
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Set gravity (default is -9.81 Z)
bpy.context.scene.gravity = (0, 0, -9.81)

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

print("Mast construction complete. Simulation ready for 100 frames.")