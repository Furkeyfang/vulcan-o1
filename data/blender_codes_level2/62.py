import bpy
import math
from mathutils import Vector

# ==================== CLEAR SCENE ====================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ==================== PARAMETERS ====================
# From parameter_summary
truss_length = 6.0
truss_height = 0.5
panel_count = 6
panel_length = truss_length / panel_count
member_cross = 0.1

deck_length = 6.0
deck_width = 1.0
deck_thickness = 0.1
deck_z_base = 0.5
deck_z_center = deck_z_base + deck_thickness/2

support_size = 0.5
support_left_pos = Vector((0.0, 0.0, support_size/2))
support_right_pos = Vector((truss_length, 0.0, support_size/2))

load_mass_kg = 400.0
gravity = 9.81
load_force_N = load_mass_kg * gravity

# Joint coordinates
top_joints = [Vector((i*panel_length, 0.0, deck_z_base)) for i in range(panel_count+1)]
bottom_joints = [Vector((i*panel_length, 0.0, 0.0)) for i in range(panel_count+1)]

# Store objects for constraint creation
truss_objects = []
deck_objects = []
support_objects = []

# ==================== SUPPORT FUNCTIONS ====================
def create_member_between(p1, p2, name):
    """Create a truss member cube between two points"""
    direction = p2 - p1
    length = direction.length
    center = (p1 + p2) / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.active_object
    obj.name = name
    
    # Scale: cross-section 0.1×0.1, length as needed
    obj.scale = (member_cross/2, member_cross/2, length/2)
    
    # Rotate to align with direction
    if length > 0.0001:
        up = Vector((0, 0, 1))
        rot_quat = direction.to_track_quat('Z', 'Y')
        obj.rotation_euler = rot_quat.to_euler()
    
    # Rigid body (active by default)
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.mass = 1.0  # Will be overridden by density
    obj.rigid_body.use_margin = True
    obj.rigid_body.collision_margin = 0.001
    
    # Material (steel-like properties)
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="Steel")
        mat.diffuse_color = (0.6, 0.6, 0.7, 1.0)
        obj.data.materials.append(mat)
    
    truss_objects.append(obj)
    return obj

def create_fixed_constraint(obj_a, obj_b):
    """Create a fixed constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return constraint

# ==================== CREATE SUPPORTS ====================
# Left support
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_left_pos)
left_support = bpy.context.active_object
left_support.name = "Support_Left"
left_support.scale = (support_size/2, support_size/2, support_size/2)
bpy.ops.rigidbody.object_add()
left_support.rigid_body.type = 'PASSIVE'
left_support.rigid_body.collision_shape = 'BOX'
support_objects.append(left_support)

# Right support  
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_right_pos)
right_support = bpy.context.active_object
right_support.name = "Support_Right"
right_support.scale = (support_size/2, support_size/2, support_size/2)
bpy.ops.rigidbody.object_add()
right_support.rigid_body.type = 'PASSIVE'
right_support.rigid_body.collision_shape = 'BOX'
support_objects.append(right_support)

# ==================== CREATE TRUSS MEMBERS ====================
# Store members by joint for constraint creation
joint_members = {f"T{i}": [] for i in range(panel_count+1)}
joint_members.update({f"B{i}": [] for i in range(panel_count+1)})

# Bottom chord
for i in range(panel_count):
    obj = create_member_between(bottom_joints[i], bottom_joints[i+1], f"BottomChord_{i}")
    joint_members[f"B{i}"].append(obj)
    joint_members[f"B{i+1}"].append(obj)

# Top chord  
for i in range(panel_count):
    obj = create_member_between(top_joints[i], top_joints[i+1], f"TopChord_{i}")
    joint_members[f"T{i}"].append(obj)
    joint_members[f"T{i+1}"].append(obj)

# Diagonals (alternating pattern)
for i in range(0, panel_count, 2):  # Even indices: bottom to top
    obj = create_member_between(bottom_joints[i], top_joints[i+1], f"Diagonal_BT_{i}")
    joint_members[f"B{i}"].append(obj)
    joint_members[f"T{i+1}"].append(obj)

for i in range(1, panel_count, 2):  # Odd indices: top to bottom  
    obj = create_member_between(top_joints[i], bottom_joints[i+1], f"Diagonal_TB_{i}")
    joint_members[f"T{i}"].append(obj)
    joint_members[f"B{i+1}"].append(obj)

# Verticals (at remaining joints)
vertical_indices = [1, 3, 5]  # B1, B3, B5
for i in vertical_indices:
    obj = create_member_between(bottom_joints[i], top_joints[i], f"Vertical_{i}")
    joint_members[f"B{i}"].append(obj)
    joint_members[f"T{i}"].append(obj)

# ==================== CREATE DECK ====================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=Vector((truss_length/2, 0.0, deck_z_center)))
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = (deck_length/2, deck_width/2, deck_thickness/2)
bpy.ops.rigidbody.object_add()
deck.rigid_body.collision_shape = 'BOX'
deck.rigid_body.mass = load_mass_kg  # Apply the 400kg load as mass
deck_objects.append(deck)

# Add material
if not deck.data.materials:
    mat = bpy.data.materials.new(name="Deck_Material")
    mat.diffuse_color = (0.8, 0.7, 0.6, 1.0)
    deck.data.materials.append(mat)

# ==================== CREATE CONSTRAINTS ====================
# Constraint all truss joints
for joint_name, members in joint_members.items():
    if len(members) >= 2:
        # Create constraints between all pairs at this joint
        for i in range(len(members)):
            for j in range(i+1, len(members)):
                create_fixed_constraint(members[i], members[j])

# Constraint supports to bottom chord ends
# Find bottom chord end members
bottom_end_members = [obj for obj in truss_objects if "BottomChord_0" in obj.name or 
                     "BottomChord_5" in obj.name or  # Last bottom chord segment
                     "Diagonal_BT_0" in obj.name]    # First diagonal

for member in bottom_end_members:
    # Check if member is near left support
    if (member.location - support_left_pos).length < 1.0:
        create_fixed_constraint(member, left_support)
    # Check if member is near right support  
    if (member.location - support_right_pos).length < 1.0:
        create_fixed_constraint(member, right_support)

# Constraint deck to top chord joints
# Create multiple constraints along deck length
for i in range(panel_count+1):
    # Find top chord members at this joint
    top_members = joint_members[f"T{i}"]
    if top_members:
        # Constraint first top member to deck (simplified - in reality would be multiple points)
        create_fixed_constraint(top_members[0], deck)

# ==================== SET PHYSICS PROPERTIES ====================
# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -gravity)

# Set rigid body world settings for stability
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Set material density for truss members (steel ≈ 7850 kg/m³)
# But make it stiff and lightweight relative to load
for obj in truss_objects:
    if obj.rigid_body:
        volume = (obj.scale.x*2) * (obj.scale.y*2) * (obj.scale.z*2)  # Approximate
        obj.rigid_body.mass = volume * 100.0  # Reduced density for stability

# Ensure supports are truly fixed
for support in support_objects:
    support.rigid_body.kinematic = True  # Absolutely immovable

print(f"Structure created with {len(truss_objects)} truss members")
print(f"Load: {load_mass_kg}kg ({load_force_N:.1f}N) applied to deck")
print(f"Deck pressure: {pressure_Pa:.1f} Pa")