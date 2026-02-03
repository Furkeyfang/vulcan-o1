import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_length = 6.0
truss_height = 1.0
truss_width = 1.5
cross_section = 0.1
num_panels = 5
panel_length = span_length / num_panels
bottom_chord_z = 0.0
top_chord_z = truss_height
left_truss_y = -truss_width / 2
right_truss_y = truss_width / 2
total_load_kg = 500.0
gravity = 9.81
total_force_n = total_load_kg * gravity
mass_per_top_chord_segment = total_load_kg / (num_panels * 2)  # Distributed across top chords of both trusses

# Create material for visualization
mat = bpy.data.materials.new(name="TrussMaterial")
mat.diffuse_color = (0.2, 0.4, 0.8, 1.0)

def create_beam(start, end, name, is_top_chord=False):
    """Create a beam between two points with proper orientation"""
    # Calculate beam properties
    vec = Vector(end) - Vector(start)
    length = vec.length
    center = (Vector(start) + Vector(end)) / 2
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (length / 2, cross_section / 2, cross_section / 2)
    
    # Position at center
    beam.location = center
    
    # Rotate to align with beam direction
    if length > 0.001:  # Avoid division by zero
        # Calculate rotation to align X-axis with beam direction
        beam.rotation_mode = 'QUATERNION'
        x_axis = Vector((1, 0, 0))
        rot_quat = x_axis.rotation_difference(vec.normalized())
        beam.rotation_quaternion = rot_quat
    
    # Apply material
    if beam.data.materials:
        beam.data.materials[0] = mat
    else:
        beam.data.materials.append(mat)
    
    # Add rigid body properties
    bpy.ops.rigidbody.object_add()
    
    # Set mass for top chord members only
    if is_top_chord:
        beam.rigid_body.mass = mass_per_top_chord_segment
        beam.rigid_body.type = 'ACTIVE'
    else:
        beam.rigid_body.mass = 0.1  # Minimal mass for non-load-bearing members
        beam.rigid_body.type = 'ACTIVE'
    
    return beam

def create_fixed_constraint(obj1, obj2):
    """Create a fixed constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj1.name}_{obj2.name}"
    constraint.location = (Vector(obj1.location) + Vector(obj2.location)) / 2
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    
    # Hide the constraint empty
    constraint.hide_viewport = True
    constraint.hide_render = True

# Generate node positions for left truss (Y = left_truss_y)
nodes_bottom_left = []
nodes_top_left = []
for i in range(num_panels + 1):
    x = -span_length/2 + i * panel_length
    nodes_bottom_left.append((x, left_truss_y, bottom_chord_z))
    nodes_top_left.append((x, left_truss_y, top_chord_z))

# Generate node positions for right truss (Y = right_truss_y)
nodes_bottom_right = []
nodes_top_right = []
for i in range(num_panels + 1):
    x = -span_length/2 + i * panel_length
    nodes_bottom_right.append((x, right_truss_y, bottom_chord_z))
    nodes_top_right.append((x, right_truss_y, top_chord_z))

# Storage for created beams
beams = []

# Create left truss
print("Creating left truss...")
for i in range(num_panels):
    # Bottom chord
    beam = create_beam(nodes_bottom_left[i], nodes_bottom_left[i+1], 
                      f"BottomChord_Left_{i}", is_top_chord=False)
    beams.append(beam)
    
    # Top chord
    beam = create_beam(nodes_top_left[i], nodes_top_left[i+1], 
                      f"TopChord_Left_{i}", is_top_chord=True)
    beams.append(beam)

# Create verticals for left truss
for i in range(num_panels + 1):
    beam = create_beam(nodes_bottom_left[i], nodes_top_left[i], 
                      f"Vertical_Left_{i}", is_top_chord=False)
    beams.append(beam)

# Create diagonals for left truss (Pratt configuration)
for i in range(num_panels):
    if i < num_panels - 1:  # Diagonals sloping downward from left to right
        beam = create_beam(nodes_top_left[i], nodes_bottom_left[i+1], 
                          f"Diagonal_Left_{i}", is_top_chord=False)
        beams.append(beam)

# Create right truss
print("Creating right truss...")
for i in range(num_panels):
    # Bottom chord
    beam = create_beam(nodes_bottom_right[i], nodes_bottom_right[i+1], 
                      f"BottomChord_Right_{i}", is_top_chord=False)
    beams.append(beam)
    
    # Top chord
    beam = create_beam(nodes_top_right[i], nodes_top_right[i+1], 
                      f"TopChord_Right_{i}", is_top_chord=True)
    beams.append(beam)

# Create verticals for right truss
for i in range(num_panels + 1):
    beam = create_beam(nodes_bottom_right[i], nodes_top_right[i], 
                      f"Vertical_Right_{i}", is_top_chord=False)
    beams.append(beam)

# Create diagonals for right truss (Pratt configuration)
for i in range(num_panels):
    if i < num_panels - 1:  # Diagonals sloping downward from left to right
        beam = create_beam(nodes_top_right[i], nodes_bottom_right[i+1], 
                          f"Diagonal_Right_{i}", is_top_chord=False)
        beams.append(beam)

# Create transverse members connecting left and right trusses
print("Creating transverse members...")
for i in range(num_panels + 1):
    # Bottom transverse
    beam = create_beam(nodes_bottom_left[i], nodes_bottom_right[i], 
                      f"Transverse_Bottom_{i}", is_top_chord=False)
    beams.append(beam)
    
    # Top transverse
    beam = create_beam(nodes_top_left[i], nodes_top_right[i], 
                      f"Transverse_Top_{i}", is_top_chord=False)
    beams.append(beam)

# Create fixed supports at ends (set as passive rigid bodies)
print("Creating fixed supports...")
support_locations = [
    nodes_bottom_left[0], nodes_bottom_left[-1],
    nodes_bottom_right[0], nodes_bottom_right[-1]
]

for i, loc in enumerate(support_locations):
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=loc)
    support = bpy.context.active_object
    support.name = f"Support_{i}"
    bpy.ops.rigidbody.object_add()
    support.rigid_body.type = 'PASSIVE'
    support.hide_viewport = True
    support.hide_render = True

# Create constraints between adjacent beams at joints
print("Creating fixed constraints...")
# This would require detecting adjacent beams at each joint
# For simplicity, we'll create constraints between beams sharing nodes

# Group beams by their endpoints (simplified approach)
joint_tolerance = 0.01
beams_by_endpoint = {}

for beam in beams:
    # Get beam endpoints (simplified - assumes beam is aligned with local X axis)
    length = beam.scale.x * 2  # Original scale was length/2
    dir_vec = Vector((1, 0, 0))
    dir_vec.rotate(beam.rotation_quaternion)
    
    end1 = Vector(beam.location) - dir_vec * length / 2
    end2 = Vector(beam.location) + dir_vec * length / 2
    
    # Round to tolerance for comparison
    key1 = (round(end1.x / joint_tolerance) * joint_tolerance,
            round(end1.y / joint_tolerance) * joint_tolerance,
            round(end1.z / joint_tolerance) * joint_tolerance)
    
    key2 = (round(end2.x / joint_tolerance) * joint_tolerance,
            round(end2.y / joint_tolerance) * joint_tolerance,
            round(end2.z / joint_tolerance) * joint_tolerance)
    
    if key1 not in beams_by_endpoint:
        beams_by_endpoint[key1] = []
    beams_by_endpoint[key1].append(beam)
    
    if key2 not in beams_by_endpoint:
        beams_by_endpoint[key2] = []
    beams_by_endpoint[key2].append(beam)

# Create constraints for beams sharing endpoints
for joint_key, joint_beams in beams_by_endpoint.items():
    if len(joint_beams) > 1:
        # Create constraints between first beam and all others
        for i in range(1, len(joint_beams)):
            create_fixed_constraint(joint_beams[0], joint_beams[i])

# Set up physics world
bpy.context.scene.gravity = (0, 0, -gravity)

print(f"Pratt truss bridge deck created with {len(beams)} members")
print(f"Total load: {total_load_kg}kg ({total_force_n}N) distributed across top chords")
print("Structure ready for static analysis")