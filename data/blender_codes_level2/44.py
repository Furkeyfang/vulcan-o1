import bpy
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
x_span = 7.0
z_height = 1.5
y_depth = 0.3
num_bays = 6
num_top_nodes = 7
num_bottom_nodes = 7
bay_width = x_span / num_bays
diagonal_length = math.sqrt(bay_width**2 + z_height**2)
member_xsection = 0.3
total_load = 8825.85
load_per_segment = total_load / num_bays
gravity = 9.80665

# Generate node positions
top_nodes = []
bottom_nodes = []
for i in range(num_top_nodes):
    x_pos = i * bay_width
    top_nodes.append(Vector((x_pos, 0, z_height)))
    bottom_nodes.append(Vector((x_pos, 0, 0)))

# Store created members for constraint creation
members_dict = {}  # node_position -> list of member objects

def create_member(name, start_pos, end_pos, member_type="chord"):
    """Create a cuboid member between two points"""
    # Calculate member properties
    direction = end_pos - start_pos
    length = direction.length
    midpoint = (start_pos + end_pos) / 2
    
    # Create cube and scale to member dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=midpoint)
    member = bpy.context.active_object
    member.name = name
    
    # Scale: cube default is 2x2x2, so we need half dimensions
    member.scale = (length/2, member_xsection/2, member_xsection/2)
    
    # Rotate to align with direction vector
    if length > 0.001:  # Avoid division by zero
        up = Vector((0, 0, 1))
        rot_quat = direction.to_track_quat('X', 'Z')
        member.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    
    # Store member reference for constraints
    for pos in [start_pos, end_pos]:
        pos_key = (round(pos.x, 4), round(pos.y, 4), round(pos.z, 4))
        if pos_key not in members_dict:
            members_dict[pos_key] = []
        members_dict[pos_key].append(member)
    
    return member

# Create top chord (6 segments)
top_members = []
for i in range(num_bays):
    member = create_member(
        f"top_chord_{i}",
        top_nodes[i],
        top_nodes[i+1],
        "top_chord"
    )
    top_members.append(member)

# Create bottom chord (6 segments)
bottom_members = []
for i in range(num_bays):
    member = create_member(
        f"bottom_chord_{i}",
        bottom_nodes[i],
        bottom_nodes[i+1],
        "bottom_chord"
    )
    bottom_members.append(member)

# Create diagonal members (Warren pattern)
diagonal_members = []
for i in range(num_bays):
    if i % 2 == 0:  # Even bays: top[i] to bottom[i+1]
        start = top_nodes[i]
        end = bottom_nodes[i+1]
        name_prefix = "diag_down"
    else:  # Odd bays: bottom[i] to top[i+1]
        start = bottom_nodes[i]
        end = top_nodes[i+1]
        name_prefix = "diag_up"
    
    member = create_member(
        f"{name_prefix}_{i}",
        start,
        end,
        "diagonal"
    )
    diagonal_members.append(member)

# Create fixed constraints at all joints
constraint_count = 0
for node_pos, member_list in members_dict.items():
    if len(member_list) > 1:
        # Create constraint between first member and all others
        base_member = member_list[0]
        for other_member in member_list[1:]:
            # Create empty for constraint
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=Vector(node_pos))
            constraint_empty = bpy.context.active_object
            constraint_empty.name = f"constraint_{constraint_count}"
            
            # Add rigid body constraint
            bpy.ops.rigidbody.constraint_add()
            constraint = constraint_empty.rigid_body_constraint
            constraint.type = 'FIXED'
            
            # Link to the two members
            constraint.object1 = base_member
            constraint.object2 = other_member
            
            constraint_count += 1

# Fix the two end supports (make first and last bottom chord members passive)
bottom_members[0].rigid_body.type = 'PASSIVE'  # Left support
bottom_members[-1].rigid_body.type = 'PASSIVE'  # Right support

# Apply distributed load to top chord members
for member in top_members:
    # Apply downward force at center of each segment
    member.rigid_body.use_gravity = True
    # In Blender, forces are applied through animation or simulation
    # For static analysis, we rely on gravity and mass distribution
    # Set appropriate mass for steel-like density (~7850 kg/m³)
    volume = (bay_width * member_xsection * member_xsection)
    mass = volume * 7850  # Steel density kg/m³
    member.rigid_body.mass = mass
    
    # Apply additional downward force to simulate load
    # Note: In Blender, we typically apply forces through animation
    # For this simulation, we'll increase mass to account for load
    load_mass = load_per_segment / gravity
    member.rigid_body.mass += load_mass

# Set up scene physics
scene = bpy.context.scene
scene.gravity = (0, 0, -gravity)
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 10
scene.frame_end = 250  # Enough frames for stabilization

print(f"Created Warren Truss with {len(top_members)} top segments, {len(bottom_members)} bottom segments, {len(diagonal_members)} diagonals")
print(f"Applied {total_load}N total load ({load_per_segment}N per top segment)")
print(f"Added {constraint_count} fixed constraints at joints")