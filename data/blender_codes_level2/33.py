import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
total_span = 12.0
truss_height = 2.0
num_panels = 6
panel_length = total_span / num_panels
beam_width = 0.2
beam_depth = 0.2
load_total_mass = 1400.0
g = 9.81
load_total_force = load_total_mass * g
num_top_nodes = num_panels + 1
load_per_node_interior = load_total_force / num_panels  # 2289 N
load_per_node_end = load_per_node_interior / 2.0        # 1144.5 N
support_nodes = [0, 6]
bottom_chord_z = 0.0
top_chord_z = truss_height

# Create node empties
node_empties = []
for i in range(num_top_nodes):
    x = i * panel_length
    # Top chord nodes
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, 0, top_chord_z))
    top_empty = bpy.context.active_object
    top_empty.name = f"Top_Node_{i}"
    # Bottom chord nodes
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, 0, bottom_chord_z))
    bot_empty = bpy.context.active_object
    bot_empty.name = f"Bot_Node_{i}"
    node_empties.append((top_empty, bot_empty))

# Define truss members as (nodeA_type, nodeA_idx, nodeB_type, nodeB_idx)
# node_type: 0=top, 1=bottom
members = []
# Top chord
for i in range(num_panels):
    members.append((0, i, 0, i+1))
# Bottom chord
for i in range(num_panels):
    members.append((1, i, 1, i+1))
# Verticals (skip ends)
for i in range(1, num_panels):
    members.append((0, i, 1, i))
# Diagonals (Howe pattern)
# Left half: bottom i to top i+1
for i in range(0, num_panels//2):
    members.append((1, i, 0, i+1))
# Right half: top i to bottom i+1 (equivalent to bottom i+1 to top i)
for i in range(num_panels//2, num_panels):
    members.append((0, i, 1, i+1))

# Function to create a beam between two points
def create_beam(pointA, pointB, name):
    # Calculate direction and length
    vec = pointB - pointA
    length = vec.length
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (beam_width, length, beam_depth)
    # Align to direction
    up = Vector((0,0,1))
    rot = vec.to_track_quat('Y', 'Z').to_matrix().to_4x4()
    beam.matrix_world = rot @ Matrix.Translation((pointA + pointB) / 2)
    return beam

# Create beams
beams = []
for idx, (typeA, iA, typeB, iB) in enumerate(members):
    nodeA = node_empties[iA][typeA].location
    nodeB = node_empties[iB][typeB].location
    beam = create_beam(nodeA, nodeB, f"Beam_{idx}")
    beams.append(beam)

# Assign rigid body properties
for empty_pair in node_empties:
    for empty in empty_pair:
        bpy.ops.rigidbody.object_add()
        empty.rigid_body.type = 'ACTIVE'
        empty.rigid_body.collision_shape = 'SPHERE'
        empty.rigid_body.mass = 1.0  # placeholder, adjusted below

for beam in beams:
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = 10.0  # approximate mass based on volume

# Set support nodes as passive
for i in support_nodes:
    node_empties[i][1].rigid_body.type = 'PASSIVE'  # bottom chord supports

# Apply loads to top chord nodes
for i, (top_empty, _) in enumerate(node_empties):
    if i == 0 or i == num_panels:
        force = load_per_node_end
    else:
        force = load_per_node_interior
    # Apply downward force via rigid body force
    top_empty.rigid_body.enabled = True
    # Force applied in world coordinates (negative Z)
    top_empty.rigid_body.force = (0, 0, -force)

# Create fixed constraints between beams and nodes
for idx, (typeA, iA, typeB, iB) in enumerate(members):
    beam = beams[idx]
    # Constraint to node A
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=node_empties[iA][typeA].location)
    const_empty_A = bpy.context.active_object
    const_empty_A.name = f"Const_A_{idx}"
    bpy.ops.rigidbody.constraint_add()
    const = const_empty_A.rigid_body_constraint
    const.type = 'FIXED'
    const.object1 = beam
    const.object2 = node_empties[iA][typeA]
    # Constraint to node B
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=node_empties[iB][typeB].location)
    const_empty_B = bpy.context.active_object
    const_empty_B.name = f"Const_B_{idx}"
    bpy.ops.rigidbody.constraint_add()
    const = const_empty_B.rigid_body_constraint
    const.type = 'FIXED'
    const.object1 = beam
    const.object2 = node_empties[iB][typeB]

# Set gravity
bpy.context.scene.gravity = (0, 0, -g)

# Optional: Set simulation end frame and run
bpy.context.scene.frame_end = 250