import bpy
import mathutils
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== PARAMETERS ==========
span_x = 5.0
width_y = 1.0
height_z = 0.5

chord_section = 0.2
brace_section = 0.2

vertical_length = height_z
chord_length = span_x
face_diag_length = (span_x**2 + height_z**2)**0.5
plan_diag_length = (span_x**2 + width_y**2)**0.5

joint_A = Vector((0.0, 0.0, 0.0))
joint_B = Vector((span_x, 0.0, 0.0))
joint_C = Vector((0.0, width_y, 0.0))
joint_D = Vector((span_x, width_y, 0.0))
joint_E = Vector((0.0, 0.0, height_z))
joint_F = Vector((span_x, 0.0, height_z))
joint_G = Vector((0.0, width_y, height_z))
joint_H = Vector((span_x, width_y, height_z))

total_load_N = 1962.0
joints_per_top = 4
force_per_joint = total_load_N / joints_per_top
material_density = 100.0
foundation_size = 0.3
foundation_height = 0.1

# ========== HELPER FUNCTIONS ==========
def create_member(start, end, section, name):
    """Create a cuboid member between two points"""
    # Calculate midpoint and length
    midpoint = (start + end) / 2
    length = (end - start).length
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=midpoint)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: length in X, section in Y and Z
    obj.scale = (length/2, section/2, section/2)  # Cube default size=2
    
    # Rotate to align with direction vector
    direction = (end - start).normalized()
    rot_quat = Vector((1,0,0)).rotation_difference(direction)
    obj.rotation_euler = rot_quat.to_euler()
    
    # Apply scale and rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.mass = material_density * (length * section * section)
    obj.rigid_body.collision_shape = 'BOX'
    
    return obj

def create_fixed_constraint(obj1, obj2, location, name):
    """Create a FIXED constraint between two objects at location"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    return empty

def create_foundation_block(location, name):
    """Create passive foundation block"""
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location + Vector((0,0,-foundation_height/2))
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (foundation_size, foundation_size, foundation_height)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'BOX'
    
    return obj

# ========== CREATE TRUSS MEMBERS ==========
members = {}

# Top chords (front/back)
members['EF'] = create_member(joint_E, joint_F, chord_section, "TopChord_Front")
members['GH'] = create_member(joint_G, joint_H, chord_section, "TopChord_Back")

# Bottom chords
members['AB'] = create_member(joint_A, joint_B, chord_section, "BottomChord_Front")
members['CD'] = create_member(joint_C, joint_D, chord_section, "BottomChord_Back")

# Verticals
members['AE'] = create_member(joint_A, joint_E, brace_section, "Vertical_AF")
members['BF'] = create_member(joint_B, joint_F, brace_section, "Vertical_BF")
members['CG'] = create_member(joint_C, joint_G, brace_section, "Vertical_CG")
members['DH'] = create_member(joint_D, joint_H, brace_section, "Vertical_DH")

# Front face diagonals (XZ plane)
members['AF'] = create_member(joint_A, joint_F, brace_section, "Diag_Front1")
members['EB'] = create_member(joint_E, joint_B, brace_section, "Diag_Front2")

# Back face diagonals (XZ plane)
members['CH'] = create_member(joint_C, joint_H, brace_section, "Diag_Back1")
members['GD'] = create_member(joint_G, joint_D, brace_section, "Diag_Back2")

# Top face diagonals (XY plane)
members['EH'] = create_member(joint_E, joint_H, brace_section, "Diag_Top1")
members['GF'] = create_member(joint_G, joint_F, brace_section, "Diag_Top2")

# Bottom face diagonals (XY plane)
members['AD'] = create_member(joint_A, joint_D, brace_section, "Diag_Bottom1")
members['CB'] = create_member(joint_C, joint_B, brace_section, "Diag_Bottom2")

# ========== CREATE FOUNDATION ==========
foundations = {}
foundations['A'] = create_foundation_block(joint_A, "Foundation_A")
foundations['B'] = create_foundation_block(joint_B, "Foundation_B")
foundations['C'] = create_foundation_block(joint_C, "Foundation_C")
foundations['D'] = create_foundation_block(joint_D, "Foundation_D")

# ========== CREATE JOINT CONSTRAINTS ==========
# Define which members meet at each joint
joint_connections = {
    'A': ['AB', 'AE', 'AF', 'AD'],
    'B': ['AB', 'BF', 'EB', 'CB'],
    'C': ['CD', 'CG', 'CH', 'CB'],
    'D': ['CD', 'DH', 'GD', 'AD'],
    'E': ['EF', 'AE', 'EB', 'EH'],
    'F': ['EF', 'BF', 'AF', 'GF'],
    'G': ['GH', 'CG', 'GD', 'GF'],
    'H': ['GH', 'DH', 'CH', 'EH']
}

# Create constraints for each joint
for joint_name, member_list in joint_connections.items():
    joint_pos = locals()[f'joint_{joint_name}']
    member_objs = [members[mb] for mb in member_list]
    
    # Connect first member to foundation if at bottom joint
    if joint_name in ['A','B','C','D']:
        create_fixed_constraint(
            member_objs[0],
            foundations[joint_name],
            joint_pos,
            f"Constraint_{joint_name}_Foundation"
        )
    
    # Connect all members in pair-wise fashion
    for i in range(len(member_objs)):
        for j in range(i+1, len(member_objs)):
            create_fixed_constraint(
                member_objs[i],
                member_objs[j],
                joint_pos,
                f"Constraint_{joint_name}_{i}_{j}"
            )

# ========== APPLY LOADS ==========
# Apply downward forces to top chord centers
top_members = [members['EF'], members['GH']]
for member in top_members:
    # Calculate force per member (half of total load on each top chord)
    force_magnitude = total_load_N / 2
    force_vector = Vector((0, 0, -force_magnitude))
    
    # Apply force at center (already at center of mass from creation)
    member.rigid_body.force = force_vector

# ========== SETUP PHYSICS WORLD ==========
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = Vector((0, 0, -9.81))
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Box truss lighting rig constructed successfully.")
print(f"Total load: {total_load_N}N distributed over top chords")
print(f"Members: {len(members)} | Constraints: {len(bpy.data.objects['Empty'])}")