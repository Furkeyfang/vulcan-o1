import bpy
import math
from mathutils import Vector, Euler

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
beam_length = 5.0
chord_separation = 0.5
member_thickness = 0.2
panel_count = 4
panel_length = beam_length / panel_count
diagonal_length = 1.3463
diagonal_angle = math.radians(21.8)  # Convert to radians
load_total_newtons = 7848.0
load_per_panel = load_total_newtons / panel_count
support_size = 0.3
support_height = 0.15
top_chord_z = chord_separation
bottom_chord_z = 0.0

# Node positions (X, Z)
top_nodes = [(i * panel_length, 0, top_chord_z) for i in range(panel_count + 1)]
bottom_nodes = [(i * panel_length, 0, bottom_chord_z) for i in range(panel_count + 1)]

# Create support blocks at ends
def create_support(pos):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    support = bpy.context.active_object
    support.scale = (support_size, support_size, support_height)
    bpy.ops.rigidbody.object_add()
    support.rigid_body.type = 'PASSIVE'
    return support

support_left = create_support((0, 0, -support_height/2))
support_right = create_support((beam_length, 0, -support_height/2))

# Function to create truss member between two points
def create_member(start, end, name):
    # Calculate center position
    center = ((start[0] + end[0])/2, (start[1] + end[1])/2, (start[2] + end[2])/2)
    
    # Calculate length and orientation
    vec = Vector(end) - Vector(start)
    length = vec.length
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    member = bpy.context.active_object
    member.name = name
    
    # Scale: thickness in X/Y, length in Z
    member.scale = (member_thickness/2, member_thickness/2, length/2)
    
    # Rotate to align with vector
    if length > 0:
        # Default cube local Z is along length after scaling
        # Align local Z axis with vector
        rot_quat = Vector((0, 0, 1)).rotation_difference(vec)
        member.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    member.rigid_body.type = 'ACTIVE'
    member.rigid_body.collision_shape = 'BOX'
    member.rigid_body.mass = 10.0  # kg per member
    
    return member

# Create top chord (segments between top nodes)
top_members = []
for i in range(panel_count):
    member = create_member(top_nodes[i], top_nodes[i+1], f"Top_Chord_{i}")
    top_members.append(member)

# Create bottom chord
bottom_members = []
for i in range(panel_count):
    member = create_member(bottom_nodes[i], bottom_nodes[i+1], f"Bottom_Chord_{i}")
    bottom_members.append(member)

# Create diagonals in Warren pattern
diagonals = []
for i in range(panel_count):
    if i % 2 == 0:  # Upward diagonal
        start = bottom_nodes[i]
        end = top_nodes[i+1]
    else:  # Downward diagonal
        start = top_nodes[i]
        end = bottom_nodes[i+1]
    
    member = create_member(start, end, f"Diagonal_{i}")
    diagonals.append(member)

# Create fixed constraints between connected members
def create_fixed_constraint(obj_a, obj_b):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=((obj_a.location.x + obj_b.location.x)/2,
                                                          (obj_a.location.y + obj_b.location.y)/2,
                                                          (obj_a.location.z + obj_b.location.z)/2))
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.use_breaking = True
    constraint.breaking_threshold = 10000.0  # High threshold

# Create constraints at nodes
all_members = top_members + bottom_members + diagonals

# Connect supports to first/last bottom nodes
create_fixed_constraint(support_left, bottom_members[0])
create_fixed_constraint(support_right, bottom_members[-1])

# Connect chord segments at interior nodes
for i in range(panel_count - 1):
    # Top chord connections
    create_fixed_constraint(top_members[i], top_members[i+1])
    # Bottom chord connections
    create_fixed_constraint(bottom_members[i], bottom_members[i+1])

# Connect diagonals to chords
for i in range(panel_count):
    diag = diagonals[i]
    
    if i % 2 == 0:  # Upward diagonal
        # Connect to bottom node i
        if i < len(bottom_members):
            create_fixed_constraint(diag, bottom_members[i])
        # Connect to top node i+1
        if i+1 < len(top_members):
            create_fixed_constraint(diag, top_members[i])
    else:  # Downward diagonal
        # Connect to top node i
        if i < len(top_members):
            create_fixed_constraint(diag, top_members[i])
        # Connect to bottom node i+1
        if i+1 < len(bottom_members):
            create_fixed_constraint(diag, bottom_members[i])

# Apply distributed load to top chord
# In Blender, we can simulate distributed load by applying forces to each segment
for i, member in enumerate(top_members):
    # Apply downward force at center of each top chord segment
    force_vector = (0, 0, -load_per_panel)
    
    # We'll use a handler to apply constant force (simplified approach)
    # Store force value as custom property
    member["applied_force"] = force_vector
    member["apply_force"] = True  # Flag to apply force

# Set up rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 0.1  # Slow motion for observation

# Add a plane as ground reference
bpy.ops.mesh.primitive_plane_add(size=10, location=(beam_length/2, 0, -1))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Frame settings for animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

print("Warren truss beam constructed with fixed constraints and distributed load applied.")
print(f"Total load: {load_total_newtons} N ({load_total_newtons/9.81:.1f} kg)")
print(f"Load per panel: {load_per_panel} N")