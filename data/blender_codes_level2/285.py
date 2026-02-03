import bpy
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
span = 8.0
start_depth = 1.5
end_depth = 0.5
num_bays = 4
member_width = 0.2
joint_tolerance = 0.01
load_mass = 500.0
load_size = 0.5
base_density = 100.0
constraint_damping = 0.5
bay_length = span / num_bays

# Node positions
bottom_nodes = [
    Vector((0.0, 0.0, 0.0)),
    Vector((2.0, 0.0, 0.0)),
    Vector((4.0, 0.0, 0.0)),
    Vector((6.0, 0.0, 0.0)),
    Vector((8.0, 0.0, 0.0))
]

top_nodes = [
    Vector((0.0, 0.0, 1.5)),
    Vector((2.0, 0.0, 1.25)),
    Vector((4.0, 0.0, 1.0)),
    Vector((6.0, 0.0, 0.75)),
    Vector((8.0, 0.0, 0.5))
]

# Function to create truss member between two points
def create_member(point_a, point_b, name):
    direction = point_b - point_a
    length = direction.length
    center = (point_a + point_b) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    member = bpy.context.active_object
    member.name = name
    member.scale = (member_width, member_width, length)
    
    # Align to direction vector
    if length > 0.001:
        member.rotation_mode = 'QUATERNION'
        z_axis = Vector((0, 0, 1))
        rot_quat = z_axis.rotation_difference(direction)
        member.rotation_quaternion = rot_quat
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    member.rigid_body.mass = base_density * (member_width**2 * length)
    member.rigid_body.use_margin = True
    member.rigid_body.collision_margin = 0.01
    
    return member

# Create bottom chord members
bottom_members = []
for i in range(num_bays):
    member = create_member(bottom_nodes[i], bottom_nodes[i+1], f"Bottom_Chord_{i}")
    bottom_members.append(member)

# Create top chord members
top_members = []
for i in range(num_bays):
    member = create_member(top_nodes[i], top_nodes[i+1], f"Top_Chord_{i}")
    top_members.append(member)

# Create vertical members
vertical_members = []
for i in range(len(bottom_nodes)):
    member = create_member(bottom_nodes[i], top_nodes[i], f"Vertical_{i}")
    vertical_members.append(member)

# Create diagonal members
diagonal_members = []
for i in range(num_bays):
    member = create_member(bottom_nodes[i], top_nodes[i+1], f"Diagonal_{i}")
    diagonal_members.append(member)

# Create joint constraints
all_members = bottom_members + top_members + vertical_members + diagonal_members
joints = []

# Create constraint at each node
for node_idx in range(len(bottom_nodes)):
    # Find all members within tolerance of this node
    connected_members = []
    for member in all_members:
        # Check if member endpoint is near node
        vertices = [member.matrix_world @ Vector(v.co) for v in member.data.vertices]
        for v in vertices:
            if (v - bottom_nodes[node_idx]).length < joint_tolerance or 
               (v - top_nodes[node_idx]).length < joint_tolerance:
                connected_members.append(member)
                break
    
    # Create fixed constraints between first member and all others
    if len(connected_members) > 1:
        base_member = connected_members[0]
        for other_member in connected_members[1:]:
            # Create constraint empty
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=bottom_nodes[node_idx] if node_idx < len(bottom_nodes) else top_nodes[node_idx-5])
            constraint_obj = bpy.context.active_object
            constraint_obj.name = f"Joint_Constraint_{node_idx}_{connected_members.index(other_member)}"
            
            # Add rigid body constraint
            bpy.ops.rigidbody.constraint_add()
            constraint_obj.rigid_body_constraint.type = 'FIXED'
            constraint_obj.rigid_body_constraint.object1 = base_member
            constraint_obj.rigid_body_constraint.object2 = other_member
            constraint_obj.rigid_body_constraint.use_breaking = False
            constraint_obj.rigid_body_constraint.disable_collisions = True
            constraint_obj.rigid_body_constraint.damping = constraint_damping
            joints.append(constraint_obj)

# Create anchor (first joint is passive)
anchor_members = []
for member in all_members:
    # Check if member connects to origin
    vertices = [member.matrix_world @ Vector(v.co) for v in member.data.vertices]
    for v in vertices:
        if (v - bottom_nodes[0]).length < joint_tolerance:
            anchor_members.append(member)
            break

for member in anchor_members:
    member.rigid_body.type = 'PASSIVE'

# Create load mass at free end
load_location = bottom_nodes[-1] + Vector((0, 0, -load_size/2))
bpy.ops.mesh.primitive_cube_add(size=load_size, location=load_location)
load = bpy.context.active_object
load.name = "Load_Mass"
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.use_margin = True
load.rigid_body.collision_margin = 0.05

# Constrain load to free end joint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=bottom_nodes[-1])
load_constraint = bpy.context.active_object
load_constraint.name = "Load_Constraint"
bpy.ops.rigidbody.constraint_add()
load_constraint.rigid_body_constraint.type = 'FIXED'
load_constraint.rigid_body_constraint.object1 = load
# Find a member at free end for constraint
free_end_member = None
for member in all_members:
    vertices = [member.matrix_world @ Vector(v.co) for v in member.data.vertices]
    for v in vertices:
        if (v - bottom_nodes[-1]).length < joint_tolerance:
            free_end_member = member
            break
    if free_end_member:
        break

if free_end_member:
    load_constraint.rigid_body_constraint.object2 = free_end_member
    load_constraint.rigid_body_constraint.disable_collisions = True
    load_constraint.rigid_body_constraint.damping = constraint_damping

# Configure world physics
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 300

print("Cantilever truss construction complete. Taper:", start_depth, "m to", end_depth, "m over", span, "m span.")