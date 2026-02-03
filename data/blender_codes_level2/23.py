import bpy
import math

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Parameters from summary
total_length = 6.0
chord_length_segment = 1.0
chord_width = 0.2
chord_height = 0.2
truss_height = 1.0
member_cross_section = 0.2
diagonal_length = 1.414
vertical_length = 1.0
load_mass_kg = 350.0
load_force_newton = 3433.5
num_bays = 6
num_segments_chord = 6
num_verticals = 7
num_diagonals = 5
support_positions = [0.0, 6.0]
load_position_x = 3.0
load_position_z = 1.0
material_density = 7850.0

# 3. Helper function to create a box with rigid body
def create_box(name, loc, dim, rb_type='ACTIVE', density=7850.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dim[0]/2, dim[1]/2, dim[2]/2)  # Cube default 2x2x2, so half dim
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rb_type
    obj.rigid_body.mass = density * (dim[0] * dim[1] * dim[2])
    return obj

# 4. Create bottom chord segments
bottom_chords = []
for i in range(num_segments_chord):
    x_center = i * chord_length_segment + chord_length_segment / 2
    loc = (x_center, 0.0, 0.0)
    dim = (chord_length_segment, chord_width, chord_height)
    rb_type = 'PASSIVE' if x_center - chord_length_segment/2 in support_positions else 'ACTIVE'
    obj = create_box(f"bottom_chord_{i}", loc, dim, rb_type, material_density)
    bottom_chords.append(obj)

# 5. Create top chord segments
top_chords = []
for i in range(num_segments_chord):
    x_center = i * chord_length_segment + chord_length_segment / 2
    loc = (x_center, 0.0, truss_height)
    dim = (chord_length_segment, chord_width, chord_height)
    obj = create_box(f"top_chord_{i}", loc, dim, 'ACTIVE', material_density)
    top_chords.append(obj)

# 6. Create vertical members
verticals = []
for i in range(num_verticals):
    x_pos = i * chord_length_segment
    loc = (x_pos, 0.0, truss_height / 2)
    dim = (member_cross_section, member_cross_section, vertical_length)
    rb_type = 'PASSIVE' if x_pos in support_positions else 'ACTIVE'
    obj = create_box(f"vertical_{i}", loc, dim, rb_type, material_density)
    verticals.append(obj)

# 7. Create diagonal members (alternating pattern)
diagonals = []
for i in range(num_diagonals):
    x_center = i * chord_length_segment + chord_length_segment / 2
    loc = (x_center, 0.0, truss_height / 2)
    dim = (member_cross_section, member_cross_section, diagonal_length)
    obj = create_box(f"diagonal_{i}", loc, dim, 'ACTIVE', material_density)
    # Rotate 45° about Y-axis, alternating direction
    if i % 2 == 0:  # bottom-left to top-right
        obj.rotation_euler = (0, -math.radians(45), 0)
    else:            # top-left to bottom-right
        obj.rotation_euler = (0, math.radians(45), 0)
    diagonals.append(obj)

# 8. Create fixed constraints at all nodes
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"fixed_{obj_a.name}_{obj_b.name}"
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    # Position constraint at midpoint between objects (approximate; in reality should be at joint)
    # For simplicity, place at obj_a location; joints are at member ends, so we'd need per-joint.
    # Instead, we'll connect each member to a common empty at each node (better).
    return constraint

# 9. Create empty at each node for accurate joint positioning
node_empties = []
for i in range(num_verticals):
    x_pos = i * chord_length_segment
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x_pos, 0.0, 0.0))
    empty = bpy.context.active_object
    empty.name = f"node_{i}_bottom"
    node_empties.append(empty)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x_pos, 0.0, truss_height))
    empty = bpy.context.active_object
    empty.name = f"node_{i}_top"
    node_empties.append(empty)

# 10. Parent each member end to corresponding node empty (using vertex groups would be complex).
# Instead, we'll create fixed constraints between members that share a node.
# For each node i (0 to 6):
for i in range(num_verticals):
    # Collect members meeting at bottom node i
    members_at_node = []
    if i < num_segments_chord:  # bottom chord segment left end
        members_at_node.append(bottom_chords[i])
    if i > 0:  # bottom chord segment right end (previous segment)
        members_at_node.append(bottom_chords[i-1])
    members_at_node.append(verticals[i])  # vertical at node
    if i < num_bays and i % 2 == 0:  # diagonal from bottom-left to top-right
        members_at_node.append(diagonals[i])
    if i > 0 and (i-1) % 2 == 1:  # diagonal from top-left to bottom-right (previous bay)
        members_at_node.append(diagonals[i-1])
    # Create constraints between all pairs
    for a in range(len(members_at_node)):
        for b in range(a+1, len(members_at_node)):
            add_fixed_constraint(members_at_node[a], members_at_node[b])
    
    # Top node (similar but with top chords)
    members_at_top = []
    if i < num_segments_chord:
        members_at_top.append(top_chords[i])
    if i > 0:
        members_at_top.append(top_chords[i-1])
    members_at_top.append(verticals[i])
    if i < num_bays and i % 2 == 0:
        members_at_top.append(diagonals[i])
    if i > 0 and (i-1) % 2 == 1:
        members_at_top.append(diagonals[i-1])
    for a in range(len(members_at_top)):
        for b in range(a+1, len(members_at_top)):
            add_fixed_constraint(members_at_top[a], members_at_top[b])

# 11. Apply load to top chord segment at midpoint
# Find top chord segment containing x=3.0 (segment index 2 and 3 both share node at x=3.0).
# We'll apply force to the segment whose center is closest.
load_segment_idx = int(load_position_x / chord_length_segment)  # this gives 3 for x=3.0 (segment index 3, center at 3.5)
load_obj = top_chords[load_segment_idx]
# Add force via rigid body custom force (applied every frame)
load_obj.rigid_body.use_custom_force = True
load_obj.rigid_body.custom_force = (0.0, 0.0, -load_force_newton)

# 12. Set gravity
bpy.context.scene.rigidbody_world.gravity.z = -9.81

# 13. Set frame range for simulation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

print("Warren truss gantry beam constructed. Simulation ready.")