import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
L_total = 8.0
panel_count = 4
panel_length = 2.0
top_z = 2.0
bottom_z = 0.5
vertical_gap = 1.5
diagonal_length = 2.5

cube_base_size = 0.25
chord_scale_x = 4.0
diagonal_scale_x = 5.0
cross_section_scale = 1.0

top_nodes = [(0.0, 0.0, top_z), (2.0, 0.0, top_z), (4.0, 0.0, top_z), (6.0, 0.0, top_z), (8.0, 0.0, top_z)]
bottom_nodes = [(0.0, 0.0, bottom_z), (2.0, 0.0, bottom_z), (4.0, 0.0, bottom_z), (6.0, 0.0, bottom_z), (8.0, 0.0, bottom_z)]

load_mass_kg = 800.0
load_force_N = 7848.0
load_position = (4.0, 0.0, top_z)

gravity = -9.81
constraint_iterations = 50

# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, gravity)

# Function to create a beam between two points
def create_beam(start, end, name, scale_x, is_passive=False):
    """Create a cube scaled to length, rotated to point from start to end"""
    # Calculate midpoint and direction
    start_vec = Vector(start)
    end_vec = Vector(end)
    mid = (start_vec + end_vec) * 0.5
    direction = end_vec - start_vec
    length = direction.length
    
    # Create base cube (size=0.25 gives 0.5m side)
    bpy.ops.mesh.primitive_cube_add(size=cube_base_size, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: X for length, Y/Z for cross-section
    obj.scale = (scale_x, cross_section_scale, cross_section_scale)
    
    # Rotate to align with direction
    if length > 0.001:
        # Default cube forward is +X
        x_axis = Vector((1.0, 0.0, 0.0))
        rot_quat = x_axis.rotation_difference(direction)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot_quat
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE' if is_passive else 'ACTIVE'
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.mass = length * 0.5 * 0.5 * 7850  # Steel density kg/m³ * volume
    
    return obj

# Create chord members
top_chords = []
for i in range(panel_count):
    start = top_nodes[i]
    end = top_nodes[i+1]
    obj = create_beam(start, end, f"Top_Chord_{i}", chord_scale_x, is_passive=False)
    top_chords.append(obj)

bottom_chords = []
for i in range(panel_count):
    start = bottom_nodes[i]
    end = bottom_nodes[i+1]
    # First and last bottom chords are supports (passive)
    is_passive = (i == 0 or i == panel_count-1)
    obj = create_beam(start, end, f"Bottom_Chord_{i}", chord_scale_x, is_passive=is_passive)
    bottom_chords.append(obj)

# Create diagonal members
diagonals = []
for i in range(panel_count):
    if i % 2 == 0:  # Even: from top-left to bottom-right
        start = top_nodes[i]
        end = bottom_nodes[i+1]
    else:           # Odd: from bottom-left to top-right
        start = bottom_nodes[i]
        end = top_nodes[i+1]
    
    obj = create_beam(start, end, f"Diagonal_{i}", diagonal_scale_x, is_passive=False)
    diagonals.append(obj)

# Create load object (heavy cube at midpoint)
bpy.ops.mesh.primitive_cube_add(size=0.25, location=load_position)
load_obj = bpy.context.active_object
load_obj.name = "Load"
load_obj.scale = (0.5, 0.5, 0.5)  # 0.5m cube
bpy.ops.rigidbody.object_add()
load_obj.rigid_body.type = 'ACTIVE'
load_obj.rigid_body.mass = load_mass_kg
load_obj.rigid_body.collision_shape = 'BOX'

# Create fixed constraints at all nodes
def add_fixed_constraint(obj_a, obj_b, node_pos):
    """Add a fixed constraint between two objects at a node"""
    # Create empty at node for constraint reference
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=node_pos)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.use_breaking = True
    constraint.breaking_threshold = 10000  # High threshold
    
    # Parent empty to one object (for organization)
    empty.parent = obj_a

# Connect beams at top nodes
for i, node in enumerate(top_nodes):
    beams_at_node = []
    # Top chord to left
    if i > 0:
        beams_at_node.append(top_chords[i-1])
    # Top chord to right
    if i < panel_count:
        beams_at_node.append(top_chords[i]) if i < panel_count else None
    # Diagonals
    if i < panel_count and i % 2 == 0:  # Even diagonal starts here
        beams_at_node.append(diagonals[i])
    if i > 0 and (i-1) % 2 == 1:  # Odd diagonal ends here
        beams_at_node.append(diagonals[i-1])
    
    # Add constraints between first beam and others
    if len(beams_at_node) > 1:
        for j in range(1, len(beams_at_node)):
            add_fixed_constraint(beams_at_node[0], beams_at_node[j], node)

# Connect beams at bottom nodes
for i, node in enumerate(bottom_nodes):
    beams_at_node = []
    # Bottom chord to left
    if i > 0:
        beams_at_node.append(bottom_chords[i-1])
    # Bottom chord to right
    if i < panel_count:
        beams_at_node.append(bottom_chords[i]) if i < panel_count else None
    # Diagonals
    if i < panel_count and i % 2 == 1:  # Odd diagonal starts here
        beams_at_node.append(diagonals[i])
    if i > 0 and (i-1) % 2 == 0:  # Even diagonal ends here
        beams_at_node.append(diagonals[i-1])
    
    if len(beams_at_node) > 1:
        for j in range(1, len(beams_at_node)):
            add_fixed_constraint(beams_at_node[0], beams_at_node[j], node)

# Connect load to top chord at midpoint (node 2)
load_node = top_nodes[2]  # X=4.0
add_fixed_constraint(top_chords[1], load_obj, load_node)  # Top_Chord_1 is between nodes 2-3
add_fixed_constraint(top_chords[2], load_obj, load_node)  # Top_Chord_2 is between nodes 3-4

# Set physics scene settings for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = constraint_iterations
bpy.context.scene.frame_end = 250  # Simulate for 250 frames

print("Warren Truss crane beam created with fixed constraints.")
print(f"Load: {load_mass_kg} kg ({load_force_N} N) applied at {load_position}")