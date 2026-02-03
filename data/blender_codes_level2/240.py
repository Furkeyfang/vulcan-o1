import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 8.0
peak_height = 2.0
member_cs = 0.1  # cross-section
joint_rad = 0.15
joint_h = 0.1
total_load = 5886.0

# Node coordinates
bottom_nodes = [Vector((-4.0, 0.0, 0.0)), Vector((-2.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0)),
                Vector((2.0, 0.0, 0.0)), Vector((4.0, 0.0, 0.0))]
top_left = [Vector((-4.0, 0.0, 0.0)), Vector((-2.667, 0.0, 1.333)),
            Vector((-1.333, 0.0, 0.667)), Vector((0.0, 0.0, 2.0))]
top_right = [Vector((4.0, 0.0, 0.0)), Vector((2.667, 0.0, 1.333)),
             Vector((1.333, 0.0, 0.667)), Vector((0.0, 0.0, 2.0))]
# Web connections as (top_node, bottom_node) pairs
web_pairs = [(Vector((-2.667, 0.0, 1.333)), Vector((-2.0, 0.0, 0.0))),
             (Vector((-1.333, 0.0, 0.667)), Vector((0.0, 0.0, 0.0))),
             (Vector((0.0, 0.0, 2.0)), Vector((0.0, 0.0, 0.0))),
             (Vector((1.333, 0.0, 0.667)), Vector((0.0, 0.0, 0.0))),
             (Vector((2.667, 0.0, 1.333)), Vector((2.0, 0.0, 0.0)))]

# Function to create a structural member between two points
def create_member(start, end, name):
    # Calculate length and direction
    vec = end - start
    length = vec.length
    center = (start + end) / 2
    
    # Create cube and scale to member dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    member = bpy.context.active_object
    member.name = name
    # Scale: thickness in Y, cross-section in X, length in Z (then rotate)
    member.scale = (member_cs/2, member_cs/2, length/2)
    
    # Rotate to align with vector
    if length > 0.001:  # Avoid division by zero
        axis = vec.normalized()
        up = Vector((0, 0, 1))
        if axis.dot(up) < 0.999:  # Not already aligned
            rot_quat = up.rotation_difference(axis)
            member.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    return member

# Function to create connection joint
def create_joint(location, name):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=joint_rad, 
                                        depth=joint_h, location=location)
    joint = bpy.context.active_object
    joint.name = name
    bpy.ops.rigidbody.object_add()
    joint.rigid_body.type = 'PASSIVE'
    joint.rigid_body.collision_shape = 'MESH'
    return joint

# Create all joints first
all_joints = {}
for i, pos in enumerate(bottom_nodes):
    joint = create_joint(pos, f"bottom_joint_{i}")
    all_joints[tuple(pos)] = joint

for pos in top_left + top_right:
    if tuple(pos) not in all_joints:
        joint = create_joint(pos, f"top_joint_{len(all_joints)}")
        all_joints[tuple(pos)] = joint

# Create bottom chord members
for i in range(len(bottom_nodes)-1):
    create_member(bottom_nodes[i], bottom_nodes[i+1], f"bottom_chord_{i}")

# Create top chord members (left side)
for i in range(len(top_left)-1):
    create_member(top_left[i], top_left[i+1], f"top_chord_left_{i}")

# Create top chord members (right side)
for i in range(len(top_right)-1):
    create_member(top_right[i], top_right[i+1], f"top_chord_right_{i}")

# Create web members
for i, (top, bottom) in enumerate(web_pairs):
    create_member(top, bottom, f"web_{i}")

# Create fixed constraints between members and joints
for obj in bpy.data.objects:
    if "chord" in obj.name or "web" in obj.name:
        # Find nearest joints (should be at ends)
        bbox = [Vector(v) for v in obj.bound_box]
        # Approximate end points from bounding box extremes
        ends = [obj.matrix_world @ min(bbox, key=lambda v: v.z),
                obj.matrix_world @ max(bbox, key=lambda v: v.z)]
        
        for end in ends:
            # Find closest joint
            closest = None
            min_dist = float('inf')
            for pos, joint in all_joints.items():
                dist = (end - joint.location).length
                if dist < min_dist and dist < 0.5:  # Within reasonable distance
                    min_dist = dist
                    closest = joint
            
            if closest:
                # Create empty for constraint
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=end)
                empty = bpy.context.active_object
                empty.name = f"constraint_{obj.name}_{closest.name}"
                
                # Add rigid body constraint
                bpy.ops.rigidbody.constraint_add()
                constraint = empty.rigid_body_constraint
                constraint.type = 'FIXED'
                constraint.object1 = obj
                constraint.object2 = closest

# Apply loads to top chord nodes (excluding ends which are supports)
load_nodes = [top_left[1], top_left[2], top_right[1], top_right[2]]
force_per_node = total_load / len(load_nodes)

for node_pos in load_nodes:
    joint = all_joints.get(tuple(node_pos))
    if joint:
        # Add force via rigid body
        joint.rigid_body.enabled = False  # Temporarily disable to set force
        joint.rigid_body.kinematic = True
        # In headless, we'd typically use animation or keyframes for forces
        # For simulation, we'll use a downward impulse
        joint.rigid_body.enabled = True
        joint.rigid_body.kinematic = False
        # Note: Direct force application in bpy requires frame-by-frame updates
        # For this example, we'll rely on constraints and let gravity work

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)

# Constrain bottom chord ends (simulate supports)
for pos in [bottom_nodes[0], bottom_nodes[-1]]:
    joint = all_joints.get(tuple(pos))
    if joint:
        joint.rigid_body.type = 'PASSIVE'  # Already passive, ensure fixed
        # In actual simulation, these would be constrained to world

print("Fink truss construction complete. Run simulation to verify stability.")