import bpy
import math
from mathutils import Vector, Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 12.0
b_width = 0.2
b_height = 0.2
u_width = 0.15
u_height = 0.15
web_sz = 0.1
peak_z = 2.5
kp_height = 2.0
kp_width = 0.15
total_load = 900.0
n_loads = 12
load_mass = 75.0
load_sz = 0.3
sim_frames = 100

# Define joint coordinates (X, Y=0, Z)
joints = {
    'A': (-span/2, 0, 0),           # Left end
    'B': (span/2, 0, 0),            # Right end
    'C': (0, 0, peak_z),           # Peak
    'D': (-span/3, 0, peak_z*2/3), # Left intermediate 1
    'E': (-span/6, 0, peak_z/3),   # Left intermediate 2
    'F': (span/6, 0, peak_z/3),    # Right intermediate 1
    'G': (span/3, 0, peak_z*2/3),  # Right intermediate 2
    'H': (-span/2, 0, 0),          # Bottom left (same as A)
    'I': (-span/3, 0, 0),          # Bottom vertical 1
    'J': (-span/6, 0, 0),          # Bottom vertical 2
    'K': (0, 0, 0),               # Center (king post base)
    'L': (span/6, 0, 0),          # Bottom vertical 3
    'M': (span/3, 0, 0),          # Bottom vertical 4
    'N': (span/2, 0, 0)           # Bottom right (same as B)
}

# Function to create beam between two points
def create_beam(start, end, name, width, height):
    # Calculate center
    center = ((start[0]+end[0])/2, (start[1]+end[1])/2, (start[2]+end[2])/2)
    
    # Calculate length and direction
    vec = Vector(end) - Vector(start)
    length = vec.length
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length in X, width in Y, height in Z
    beam.scale = (length/2, width/2, height/2)
    
    # Rotate to align with vector
    # Default cube is aligned with world axes, need to rotate
    # Calculate rotation to align local X with vector
    up = Vector((0, 0, 1))
    axis = vec.cross(up)
    angle = vec.angle(up)
    
    # If vector is parallel to up, use different method
    if angle < 0.001 or angle > 3.140:
        # Horizontal beam
        beam.rotation_euler = Euler((0, math.pi/2, 0), 'XYZ')
        # Then rotate around Z to align with direction
        horiz_angle = math.atan2(vec.y, vec.x)
        beam.rotation_euler.z = horiz_angle
    else:
        # General 3D rotation
        beam.rotation_mode = 'QUATERNION'
        beam.rotation_quaternion = vec.to_track_quat('X', 'Z')
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'
    
    return beam

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj1, obj2, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = name
    
    # Position at midpoint (for visualization)
    pos1 = Vector(obj1.location)
    pos2 = Vector(obj2.location)
    empty.location = (pos1 + pos2) * 0.5
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    return empty

# Create bottom chord (single long beam)
print("Creating bottom chord...")
bottom = create_beam(joints['A'], joints['B'], 'Bottom_Chord', b_width, b_height)

# Create upper chords (left and right)
print("Creating upper chords...")
upper_left = create_beam(joints['A'], joints['C'], 'Upper_Chord_Left', u_width, u_height)
upper_right = create_beam(joints['B'], joints['C'], 'Upper_Chord_Right', u_width, u_height)

# Create king post
print("Creating king post...")
king = create_beam(joints['K'], joints['C'], 'King_Post', kp_width, kp_width)
# King post is vertical, adjust scaling (height is along Z)
king.scale = (kp_width/2, kp_width/2, kp_height/2)
king.location = (0, 0, kp_height/2)

# Create web verticals
print("Creating web verticals...")
web_verts = []
web_names = ['Web_Vert_I', 'Web_Vert_J', 'Web_Vert_K', 'Web_Vert_L', 'Web_Vert_M']
vert_starts = ['I', 'J', 'K', 'L', 'M']
vert_ends = ['D', 'E', 'C', 'F', 'G']

for i in range(5):
    beam = create_beam(joints[vert_starts[i]], joints[vert_ends[i]], 
                      web_names[i], web_sz, web_sz)
    web_verts.append(beam)

# Create web diagonals for triangulation
print("Creating web diagonals...")
diagonals = []
diag_pairs = [
    (joints['A'], joints['E'], 'Diag_AE'),
    (joints['I'], joints['C'], 'Diag_IC'),
    (joints['J'], joints['C'], 'Diag_JC'),
    (joints['K'], joints['G'], 'Diag_KG'),
    (joints['L'], joints['C'], 'Diag_LC'),
    (joints['M'], joints['C'], 'Diag_MC'),
    (joints['B'], joints['F'], 'Diag_BF')
]

for start, end, name in diag_pairs:
    beam = create_beam(start, end, name, web_sz, web_sz)
    diagonals.append(beam)

# Create fixed constraints at joints
print("Creating constraints...")
# Collect all beams
all_beams = [bottom, upper_left, upper_right, king] + web_verts + diagonals

# Create constraints for key joints (simplified - full pairwise would be many)
# Main joints: Peak (C), Left end (A), Right end (B), Center (K)
joint_beams = {
    'C': [upper_left, upper_right, king] + [web_verts[i] for i in [2]] + [diagonals[j] for j in [1,2,5,6]],
    'A': [bottom, upper_left, diagonals[0]],
    'B': [bottom, upper_right, diagonals[6]],
    'K': [bottom, king, web_verts[2]]
}

# Create constraints (simplified - just connect first two beams at each joint)
for joint, beams in joint_beams.items():
    if len(beams) >= 2:
        create_fixed_constraint(beams[0], beams[1], f"Constraint_{joint}")

# Create load weights
print("Creating load weights...")
load_spacing = span / n_loads
start_x = -span/2 + load_spacing/2

for i in range(n_loads):
    x_pos = start_x + i * load_spacing
    # Create cube slightly above bottom chord
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, b_height + load_sz/2))
    load = bpy.context.active_object
    load.name = f"Load_{i}"
    load.scale = (load_sz/2, load_sz/2, load_sz/2)
    
    # Add rigid body with mass
    bpy.ops.rigidbody.object_add()
    load.rigid_body.type = 'ACTIVE'
    load.rigid_body.mass = load_mass
    load.rigid_body.collision_shape = 'BOX'

# Setup simulation
print("Setting up simulation...")
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Set gravity (default is -9.8 Z)
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.8)

print("Truss construction complete. Ready for simulation.")