import bpy
import mathutils
from math import sqrt

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
truss_height = 6.0
num_bays = 4
cube_size = 0.5
member_length = 1.732
member_scale_x = member_length / cube_size  # 1.732 / 0.5 = 3.464
horizontal_spacing = 0.866
vertical_spacing = 1.5
lateral_force = 1962.0
simulation_frames = 100
member_density = 1000.0

# Node positions (Y, Z) with X=0
node_positions = [
    (0.0, 0.0, 0.0),           # Node0
    (horizontal_spacing, 0.0, 0.0),    # Node1
    (2*horizontal_spacing, 0.0, 0.0),  # Node2
    (0.5*horizontal_spacing, 0.0, vertical_spacing),     # Node3
    (1.5*horizontal_spacing, 0.0, vertical_spacing),     # Node4
    (0.0, 0.0, 2*vertical_spacing),    # Node5
    (horizontal_spacing, 0.0, 2*vertical_spacing),       # Node6
    (2*horizontal_spacing, 0.0, 2*vertical_spacing),     # Node7
    (0.5*horizontal_spacing, 0.0, 3*vertical_spacing),   # Node8
    (1.5*horizontal_spacing, 0.0, 3*vertical_spacing),   # Node9
    (0.0, 0.0, 4*vertical_spacing),    # Node10
    (horizontal_spacing, 0.0, 4*vertical_spacing),       # Node11
    (2*horizontal_spacing, 0.0, 4*vertical_spacing),     # Node12
]

# Member connections (indices in node_positions)
member_connections = [
    (0, 3), (3, 1), (1, 4), (4, 2),      # Bottom triangles
    (3, 5), (5, 6), (6, 3), (6, 4), (4, 7), (7, 6),  # Middle section
    (5, 8), (8, 6), (6, 9), (9, 7),      # Upper middle
    (8, 10), (10, 11), (11, 8), (11, 9), (9, 12),  # Top triangles
]

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Store created members for constraint creation
members = []

# Function to create member between two nodes
def create_member(node_a, node_b, idx):
    # Calculate midpoint and direction
    midpoint = ((node_a[0] + node_b[0]) / 2,
                (node_a[1] + node_b[1]) / 2,
                (node_a[2] + node_b[2]) / 2)
    
    # Direction vector and length
    direction = mathutils.Vector(node_b) - mathutils.Vector(node_a)
    length = direction.length
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=midpoint)
    member = bpy.context.active_object
    member.name = f"Member_{idx}"
    
    # Scale to length (local X axis)
    member.scale.x = length / cube_size
    member.scale.y = 1.0
    member.scale.z = 1.0
    bpy.ops.object.transform_apply(scale=True)
    
    # Rotate to align with direction
    if length > 0:
        quat = mathutils.Vector((1, 0, 0)).rotation_difference(direction)
        member.rotation_euler = quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    member.rigid_body.mass = member_density * (cube_size**3) * member.scale.x
    member.rigid_body.collision_shape = 'BOX'
    
    return member

# Create all members
for i, (a_idx, b_idx) in enumerate(member_connections):
    member = create_member(node_positions[a_idx], node_positions[b_idx], i)
    members.append(member)

# Create fixed constraints at joints
constraints = []
for node_idx, node_pos in enumerate(node_positions):
    # Find all members connected to this node
    connected_members = []
    for i, (a_idx, b_idx) in enumerate(member_connections):
        if node_idx == a_idx or node_idx == b_idx:
            connected_members.append(members[i])
    
    # Create constraints between connected members
    if len(connected_members) >= 2:
        for j in range(1, len(connected_members)):
            # Create empty for constraint
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=node_pos)
            constraint_empty = bpy.context.active_object
            constraint_empty.name = f"Constraint_Node{node_idx}_{j}"
            
            # Add rigid body constraint
            bpy.ops.rigidbody.constraint_add()
            constraint = constraint_empty.rigid_body_constraint
            constraint.type = 'FIXED'
            constraint.object1 = connected_members[0]
            constraint.object2 = connected_members[j]
            
            constraints.append(constraint_empty)

# Anchor bottom chord to ground
bottom_nodes = [0, 1, 2]
for node_idx in bottom_nodes:
    # Find members connected to bottom nodes
    for i, (a_idx, b_idx) in enumerate(member_connections):
        if node_idx == a_idx or node_idx == b_idx:
            # Create constraint to ground
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=node_positions[node_idx])
            anchor = bpy.context.active_object
            anchor.name = f"Anchor_Node{node_idx}"
            
            bpy.ops.rigidbody.constraint_add()
            constraint = anchor.rigid_body_constraint
            constraint.type = 'FIXED'
            constraint.object1 = ground
            constraint.object2 = members[i]

# Apply lateral force to top center node (Node11)
force_node_idx = 11
force_members = []
for i, (a_idx, b_idx) in enumerate(member_connections):
    if force_node_idx == a_idx or force_node_idx == b_idx:
        force_members.append(members[i])

# Apply force to all connected members at top center
for member in force_members:
    # Add force via rigid body
    member.rigid_body.use_gravity = True
    # Force will be applied in animation

# Set up simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Create force application via keyframes
bpy.context.scene.frame_set(1)
for member in force_members:
    member.keyframe_insert(data_path="rigid_body.kinematic", frame=1)
    member.rigid_body.kinematic = True  # Keep stationary initially

bpy.context.scene.frame_set(10)
for member in force_members:
    member.rigid_body.kinematic = False
    member.keyframe_insert(data_path="rigid_body.kinematic", frame=10)
    # Apply impulse force
    member.rigid_body.apply_force([lateral_force/len(force_members), 0, 0])
    member.keyframe_insert(data_path="rigid_body.linear_velocity", frame=10)

# Bake simulation for verification
bpy.ops.ptcache.bake_all(bake=True)