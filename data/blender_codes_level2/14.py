import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Variables from parameter summary
total_span = 14.0
vertical_height = 1.5
panel_width = 2.8
chord_section = (0.2, 0.2, 7.0)
vertical_section = (0.2, 0.2, 1.5)
diagonal_section = (0.2, 0.2, 2.0)
top_chord_z = 1.6
bottom_chord_z = 0.1
joint_x = [-7.0, -4.2, -1.4, 1.4, 4.2, 7.0]
diagonal_pairs = [(0,1), (1,2), (3,4), (4,5)]
load_mass = 2000.0
load_size = (1.0, 1.0, 0.5)
load_start_x = -6.5
load_end_x = 6.5
load_y = 0.0
load_z = 1.85

# Create collection for bridge
bridge_collection = bpy.data.collections.new("Bridge")
bpy.context.scene.collection.children.link(bridge_collection)

# Function to create member with physics
def create_member(name, location, scale, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    
    if rotation:
        obj.rotation_euler = rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'BOX'
    
    # Link to bridge collection
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    bridge_collection.objects.link(obj)
    
    return obj

# Create top chords (two 7m sections)
top_chord_left = create_member(
    "TopChord_Left",
    location=(-3.5, 0.0, top_chord_z),
    scale=(chord_section[0]/2, chord_section[1]/2, chord_section[2]/2)
)

top_chord_right = create_member(
    "TopChord_Right",
    location=(3.5, 0.0, top_chord_z),
    scale=(chord_section[0]/2, chord_section[1]/2, chord_section[2]/2)
)

# Create bottom chords
bottom_chord_left = create_member(
    "BottomChord_Left",
    location=(-3.5, 0.0, bottom_chord_z),
    scale=(chord_section[0]/2, chord_section[1]/2, chord_section[2]/2)
)

bottom_chord_right = create_member(
    "BottomChord_Right",
    location=(3.5, 0.0, bottom_chord_z),
    scale=(chord_section[0]/2, chord_section[1]/2, chord_section[2]/2)
)

# Create vertical members
vertical_members = []
for i, x in enumerate(joint_x):
    vert = create_member(
        f"Vertical_{i}",
        location=(x, 0.0, (top_chord_z + bottom_chord_z) / 2),
        scale=(vertical_section[0]/2, vertical_section[1]/2, vertical_section[2]/2)
    )
    vertical_members.append(vert)

# Create diagonal members
diagonal_members = []
for i, (bottom_idx, top_idx) in enumerate(diagonal_pairs):
    # Calculate diagonal vector
    bottom_pos = Vector((joint_x[bottom_idx], 0.0, bottom_chord_z))
    top_pos = Vector((joint_x[top_idx], 0.0, top_chord_z))
    diagonal_vec = top_pos - bottom_pos
    length = diagonal_vec.length
    
    # Midpoint
    mid = (bottom_pos + top_pos) / 2
    
    # Rotation (align Z-axis with diagonal)
    diagonal_vec.normalize()
    up = Vector((0, 0, 1))
    if diagonal_vec.dot(up) > 0.99:  # Parallel case
        rot_matrix = Matrix()
    else:
        rot_axis = up.cross(diagonal_vec)
        rot_axis.normalize()
        angle = up.angle(diagonal_vec)
        rot_matrix = Matrix.Rotation(angle, 4, rot_axis)
    
    diag = create_member(
        f"Diagonal_{i}",
        location=mid,
        scale=(diagonal_section[0]/2, diagonal_section[1]/2, length/2),
        rotation=rot_matrix.to_euler() if rot_matrix.determinant() > 0 else (0,0,0)
    )
    diagonal_members.append(diag)

# Create fixed constraints for all joints
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    bridge_collection.objects.link(constraint)

# Connect members at each joint
all_members = [top_chord_left, top_chord_right, bottom_chord_left, bottom_chord_right] + vertical_members + diagonal_members

# Connect top chords at center (joint at x=0)
add_fixed_constraint(top_chord_left, top_chord_right)

# Connect bottom chords at center
add_fixed_constraint(bottom_chord_left, bottom_chord_right)

# Connect verticals to chords at each joint
for i, vert in enumerate(vertical_members):
    # Determine which chord section this vertical connects to
    if joint_x[i] < 0:
        top_chord = top_chord_left
        bottom_chord = bottom_chord_left
    elif joint_x[i] > 0:
        top_chord = top_chord_right
        bottom_chord = bottom_chord_right
    else:  # x=0 (center)
        top_chord = top_chord_right  # Arbitrary choice
        bottom_chord = bottom_chord_right
    
    add_fixed_constraint(vert, top_chord)
    add_fixed_constraint(vert, bottom_chord)

# Connect diagonals to chords
for i, diag in enumerate(diagonal_members):
    bottom_idx, top_idx = diagonal_pairs[i]
    
    # Determine chord sections for this diagonal
    bottom_chord = bottom_chord_left if joint_x[bottom_idx] < 0 else bottom_chord_right
    top_chord = top_chord_left if joint_x[top_idx] < 0 else top_chord_right
    
    add_fixed_constraint(diag, bottom_chord)
    add_fixed_constraint(diag, top_chord)

# Create rolling load
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(load_start_x, load_y, load_z))
load = bpy.context.active_object
load.name = "RollingLoad"
load.scale = (load_size[0]/2, load_size[1]/2, load_size[2]/2)

# Add rigid body to load
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create animation for rolling motion
load.animation_data_create()
load.animation_data.action = bpy.data.actions.new(name="RollAnimation")

# Insert location keyframes
fps = 24
duration = 10  # seconds
total_frames = fps * duration

load.location = (load_start_x, load_y, load_z)
load.keyframe_insert(data_path="location", frame=1)

load.location = (load_end_x, load_y, load_z)
load.keyframe_insert(data_path="location", frame=total_frames)

# Set linear interpolation for smooth motion
for fcurve in load.animation_data.action.fcurves:
    if fcurve.data_path == "location":
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'

print("Pratt truss bridge construction complete with rolling load simulation.")