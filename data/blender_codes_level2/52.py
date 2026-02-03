import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
span = 4.0
truss_h = 0.5
panels = 4
panel_l = span / panels
cross_sec = (0.1, 0.1)
bottom_z = 0.0
top_z = truss_h
load_mass = 700.0
load_dim = (0.5, 0.5, 0.5)
load_pos = (0.0, 0.0, top_z + load_dim[2]/2)
diag_len = math.sqrt(panel_l**2 + truss_h**2)
vert_len = truss_h

# Node coordinates
bottom_nodes = [(-2.0, 0.0, bottom_z), (-1.0, 0.0, bottom_z), (0.0, 0.0, bottom_z),
                (1.0, 0.0, bottom_z), (2.0, 0.0, bottom_z)]
top_nodes = [(-2.0, 0.0, top_z), (-1.0, 0.0, top_z), (0.0, 0.0, top_z),
             (1.0, 0.0, top_z), (2.0, 0.0, top_z)]

# Helper: create beam between two points
def create_beam(p1, p2, name, scale_x):
    mid = Vector(( (p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2 ))
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (scale_x, cross_sec[0], cross_sec[1])
    
    # Align to vector between points
    vec = Vector(p2) - Vector(p1)
    if vec.length > 0:
        beam.rotation_euler = vec.to_track_quat('X', 'Z').to_euler()
    return beam

# Bottom chords (4 segments)
bottom_beams = []
for i in range(panels):
    b1 = bottom_nodes[i]
    b2 = bottom_nodes[i+1]
    beam = create_beam(b1, b2, f"BottomChord_{i}", panel_l)
    bottom_beams.append(beam)

# Top chords (4 segments)
top_beams = []
for i in range(panels):
    t1 = top_nodes[i]
    t2 = top_nodes[i+1]
    beam = create_beam(t1, t2, f"TopChord_{i}", panel_l)
    top_beams.append(beam)

# Diagonal web members (4 diagonals)
diagonals = []
for i in range(panels):
    t = top_nodes[i]
    b = bottom_nodes[i+1]
    beam = create_beam(t, b, f"Diagonal_{i}", diag_len)
    diagonals.append(beam)

# Vertical web members (3 interior verticals)
verticals = []
for i in range(1, panels):  # Skip ends
    b = bottom_nodes[i]
    t = top_nodes[i]
    beam = create_beam(b, t, f"Vertical_{i}", vert_len)
    verticals.append(beam)

# Assign rigid body physics (all passive for static structure)
all_beams = bottom_beams + top_beams + diagonals + verticals
for obj in all_beams:
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'BOX'

# Create fixed constraints at all joints
def add_fixed_constraint(obj1, obj2, location):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj1
    con.object2 = obj2

# Connect at each node
for i in range(5):
    # Bottom node connections
    beams_at_node = []
    if i < 4: beams_at_node.append(bottom_beams[i])  # Left end of segment
    if i > 0: beams_at_node.append(bottom_beams[i-1])  # Right end of segment
    if i in [1,2,3]: beams_at_node.append(verticals[i-1])  # Vertical at interior nodes
    if i > 0 and i < 5:  # Diagonal from previous top node
        if i-1 < len(diagonals): beams_at_node.append(diagonals[i-1])
    
    # Create pairwise constraints
    for j in range(len(beams_at_node)):
        for k in range(j+1, len(beams_at_node)):
            add_fixed_constraint(beams_at_node[j], beams_at_node[k], bottom_nodes[i])
    
    # Top node connections
    beams_at_node = []
    if i < 4: beams_at_node.append(top_beams[i])
    if i > 0: beams_at_node.append(top_beams[i-1])
    if i in [1,2,3]: beams_at_node.append(verticals[i-1])
    if i < 4: beams_at_node.append(diagonals[i])  # Diagonal from this top node
    
    for j in range(len(beams_at_node)):
        for k in range(j+1, len(beams_at_node)):
            add_fixed_constraint(beams_at_node[j], beams_at_node[k], top_nodes[i])

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=load_pos)
load = bpy.context.active_object
load.name = "Equipment_Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Set simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Howe Truss construction complete. Simulate with 700kg load.")