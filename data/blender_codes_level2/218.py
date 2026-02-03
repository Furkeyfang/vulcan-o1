import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 20.0
peak_height = 5.0
base_height = 3.0
support_left_x = -10.0
support_right_x = 10.0
chord_cross_section = 0.3
web_cross_section = 0.2
top_chord_segment_length = 5.0
bottom_chord_segment_length = 5.0
web_length = math.sqrt(10**2 + 2**2)  # 10.198
total_load_N = 21582.0
force_per_segment = total_load_N / 4.0
support_passive_mass = 1000.0
active_mass = 100.0
damping = 0.5
solver_iterations = 50

# Points dictionary
points = {
    'P1': Vector((support_left_x, 0.0, base_height)),
    'P2': Vector((-5.0, 0.0, base_height)),
    'P3': Vector((0.0, 0.0, base_height)),
    'P4': Vector((5.0, 0.0, base_height)),
    'P5': Vector((support_right_x, 0.0, base_height)),
    'P6': Vector((support_left_x, 0.0, base_height)),
    'P7': Vector((-5.0, 0.0, 4.0)),
    'P8': Vector((0.0, 0.0, peak_height)),
    'P9': Vector((5.0, 0.0, 4.0)),
    'P10': Vector((support_right_x, 0.0, base_height))
}

# Function to create a beam between two points
def create_beam(name, start, end, cross_section, mass, passive=False):
    # Calculate midpoint, direction, length
    mid = (start + end) / 2
    dir_vec = end - start
    length = dir_vec.length
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    # Rotate to align with direction
    # Default cube local X axis; we want it along dir_vec
    # Use rotation difference from Vector((1,0,0)) to dir_vec.normalized()
    up = Vector((0,0,1))
    rot_quat = Vector((1,0,0)).rotation_difference(dir_vec)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = rot_quat
    # Scale: X = length, Y = cross_section, Z = cross_section
    obj.scale = (length, cross_section, cross_section)
    # Apply scale
    bpy.ops.object.transform_apply(scale=True)
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if passive:
        obj.rigid_body.type = 'PASSIVE'
        obj.rigid_body.mass = support_passive_mass
    else:
        obj.rigid_body.type = 'ACTIVE'
        obj.rigid_body.mass = active_mass
    return obj

# Create bottom chords (two segments, left and right)
bottom_left = create_beam("bottom_left", points['P1'], points['P3'], chord_cross_section, active_mass, passive=True)  # left support passive
bottom_right = create_beam("bottom_right", points['P3'], points['P5'], chord_cross_section, active_mass, passive=False)
# Set leftmost segment passive, rightmost segment active? Actually both supports must be passive.
# We'll set both bottom_left and bottom_right passive at supports? But bottom_right has active interior.
# Better: split bottom chord into three segments: left passive, center active, right passive.
# Let's create three segments: P1-P2 (passive), P2-P3 (active), P3-P4 (active), P4-P5 (passive)
bottom_seg1 = create_beam("bottom_seg1", points['P1'], points['P2'], chord_cross_section, active_mass, passive=True)
bottom_seg2 = create_beam("bottom_seg2", points['P2'], points['P3'], chord_cross_section, active_mass, passive=False)
bottom_seg3 = create_beam("bottom_seg3", points['P3'], points['P4'], chord_cross_section, active_mass, passive=False)
bottom_seg4 = create_beam("bottom_seg4", points['P4'], points['P5'], chord_cross_section, active_mass, passive=True)

# Create top chords (four segments: two each side)
top_seg1 = create_beam("top_seg1", points['P6'], points['P7'], chord_cross_section, active_mass, passive=False)
top_seg2 = create_beam("top_seg2", points['P7'], points['P8'], chord_cross_section, active_mass, passive=False)
top_seg3 = create_beam("top_seg3", points['P8'], points['P9'], chord_cross_section, active_mass, passive=False)
top_seg4 = create_beam("top_seg4", points['P9'], points['P10'], chord_cross_section, active_mass, passive=False)

# Create diagonal webs
web1 = create_beam("web1", points['P2'], points['P9'], web_cross_section, active_mass, passive=False)
web2 = create_beam("web2", points['P4'], points['P7'], web_cross_section, active_mass, passive=False)

# Create fixed constraints at joints
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.constraints[-1]
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b

# Map joint points to objects
joint_map = {
    'P1': [bottom_seg1],
    'P2': [bottom_seg1, bottom_seg2, web1],
    'P3': [bottom_seg2, bottom_seg3],
    'P4': [bottom_seg3, bottom_seg4, web2],
    'P5': [bottom_seg4],
    'P6': [top_seg1],
    'P7': [top_seg1, top_seg2, web2],
    'P8': [top_seg2, top_seg3],
    'P9': [top_seg3, top_seg4, web1],
    'P10': [top_seg4]
}

# Add constraints for each joint (connect first object to all others)
for joint, objs in joint_map.items():
    if len(objs) >= 2:
        for i in range(1, len(objs)):
            add_fixed_constraint(objs[0], objs[i])

# Apply downward forces to top chord segments
force_vector = Vector((0,0,-force_per_segment))
for top in [top_seg1, top_seg2, top_seg3, top_seg4]:
    top.rigid_body.apply_force(force_vector, point=top.location)

# Set rigid body world settings for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.split_impulse_penetration_threshold = 0.05
for obj in bpy.context.scene.objects:
    if obj.rigid_body:
        obj.rigid_body.linear_damping = damping
        obj.rigid_body.angular_damping = damping

# Set frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 500