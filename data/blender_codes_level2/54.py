import bpy
import math

# 1. Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define variables from summary
span_total = 9.0
panel_lengths = [2.0, 3.0, 4.0]
chord_height = 1.5
member_cross_section = 0.1
bottom_chord_z = 0.0
top_chord_z = 1.5
joint_x_coords = [-4.5, -2.5, 0.5, 4.5]
load_mass_kg = 650.0
gravity = 9.81
load_force_newton = load_mass_kg * gravity
load_position = (0.0, 0.0, 0.0)

# 3. Create joint empties (passive rigid bodies)
joint_empties = {}
for i, x in enumerate(joint_x_coords):
    # Bottom joint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, 0, bottom_chord_z))
    empty = bpy.context.active_object
    empty.name = f"joint_bottom_{i}"
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.type = 'PASSIVE'
    empty.rigid_body.collision_shape = 'BOX'
    empty.rigid_body.use_margin = True
    empty.rigid_body.collision_margin = 0.0
    joint_empties[f"B{i}"] = empty
    
    # Top joint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, 0, top_chord_z))
    empty = bpy.context.active_object
    empty.name = f"joint_top_{i}"
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.type = 'PASSIVE'
    empty.rigid_body.collision_shape = 'BOX'
    empty.rigid_body.use_margin = True
    empty.rigid_body.collision_margin = 0.0
    joint_empties[f"T{i}"] = empty

# 4. Function to create truss member between two joints
def create_member(joint_a, joint_b, name, cross_section=0.1):
    """Create a cuboid member between two joint empties."""
    # Calculate center and orientation
    loc_a = joint_a.location
    loc_b = joint_b.location
    center = (loc_a + loc_b) / 2
    length = (loc_a - loc_b).length
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    member = bpy.context.active_object
    member.name = name
    member.scale = (length, cross_section, cross_section)
    
    # Rotate to align with vector AB
    direction = loc_b - loc_a
    rot_quat = direction.to_track_quat('X', 'Z')
    member.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    member.rigid_body.use_margin = True
    member.rigid_body.collision_margin = 0.0
    member.rigid_body.mass = 10.0  # Reasonable mass for steel
    
    # Create fixed constraints to joints
    for joint in [joint_a, joint_b]:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint.location)
        constraint_empty = bpy.context.active_object
        constraint_empty.name = f"constraint_{name}_{joint.name}"
        bpy.ops.rigidbody.constraint_add()
        constraint = constraint_empty.rigid_body_constraint
        constraint.type = 'FIXED'
        constraint.object1 = member
        constraint.object2 = joint
    
    return member

# 5. Create horizontal chords
# Bottom chord (segments between consecutive bottom joints)
for i in range(3):
    create_member(joint_empties[f"B{i}"], joint_empties[f"B{i+1}"], 
                  f"bottom_chord_{i}", member_cross_section)
# Top chord
for i in range(3):
    create_member(joint_empties[f"T{i}"], joint_empties[f"T{i+1}"], 
                  f"top_chord_{i}", member_cross_section)

# 6. Create vertical members
for i in range(4):
    create_member(joint_empties[f"B{i}"], joint_empties[f"T{i}"], 
                  f"vertical_{i}", member_cross_section)

# 7. Create diagonals (Pratt configuration)
diagonal_defs = [
    (joint_empties["T0"], joint_empties["B1"], "diag_left"),
    (joint_empties["T2"], joint_empties["B1"], "diag_mid"),
    (joint_empties["T2"], joint_empties["B3"], "diag_right")
]
for joint_a, joint_b, name in diagonal_defs:
    create_member(joint_a, joint_b, name, member_cross_section)

# 8. Apply central load
# Create load empty at center
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_position)
load_empty = bpy.context.active_object
load_empty.name = "central_load"
bpy.ops.rigidbody.object_add()
load_empty.rigid_body.type = 'ACTIVE'
load_empty.rigid_body.mass = load_mass_kg
# Apply downward force (negative Z)
load_empty.rigid_body.force = (0.0, 0.0, -load_force_newton)

# Constrain load to center bottom chord segment (between B1 and B2)
# Find the bottom chord segment containing X=0
center_segment = None
for obj in bpy.data.objects:
    if "bottom_chord_1" in obj.name:  # Segment from B1(-2.5) to B2(0.5)
        center_segment = obj
        break
if center_segment:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_position)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = "load_constraint"
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = load_empty
    constraint.object2 = center_segment

# 9. Set world gravity (standard)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

print("Pratt truss bridge with fixed joints created successfully.")