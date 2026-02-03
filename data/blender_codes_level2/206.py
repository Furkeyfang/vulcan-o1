import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 14.0
height = 2.0
bottom_z = 5.0
top_z = bottom_z + height
panels = 6
panel_width = span / panels
chord_section = (0.2, 0.2, 14.0)  # X,Y cross-section, Z=length placeholder
web_section = (0.15, 0.15, 1.0)   # X,Y cross-section, Z=length placeholder
diag_len = math.sqrt(panel_width**2 + height**2)
total_load = 1200.0 * 9.81  # 11772 N
load_per_panel = total_load / panels

# Generate joint coordinates
bottom_joints = []
top_joints = []
for i in range(panels + 1):
    x = i * panel_width
    bottom_joints.append((x, 0.0, bottom_z))
    top_joints.append((x, 0.0, top_z))

# Function to create structural member
def create_member(name, start, end, cross_xy, is_passive=False):
    """Create a beam between two points with given cross-section"""
    # Calculate midpoint and direction
    start_vec = Vector(start)
    end_vec = Vector(end)
    mid = (start_vec + end_vec) * 0.5
    direction = (end_vec - start_vec).normalized()
    length = (end_vec - start_vec).length
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: cross_xy[0,1] for width/depth, length for Z
    beam.scale = (cross_xy[0]/2, cross_xy[1]/2, length/2)
    
    # Rotate to align with direction
    # Default cube points along local Z, rotate to match world direction
    up = Vector((0, 0, 1))
    rot_quat = up.rotation_difference(direction)
    beam.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if is_passive:
        beam.rigid_body.type = 'PASSIVE'
    else:
        beam.rigid_body.type = 'ACTIVE'
        beam.rigid_body.mass = 50.0  # Estimated mass for simulation
    
    return beam

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b):
    """Create fixed constraint connecting two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link objects
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return empty

# Create bottom chords (6 segments)
bottom_chords = []
for i in range(panels):
    start = bottom_joints[i]
    end = bottom_joints[i+1]
    name = f"Bottom_Chord_{i}"
    # End segments are passive (supports)
    is_passive = (i == 0 or i == panels-1)
    chord = create_member(name, start, end, chord_section[:2], is_passive)
    bottom_chords.append(chord)

# Create top chords (6 segments)
top_chords = []
for i in range(panels):
    start = top_joints[i]
    end = top_joints[i+1]
    name = f"Top_Chord_{i}"
    chord = create_member(name, start, end, chord_section[:2], False)
    top_chords.append(chord)

# Create vertical members (7 members)
verticals = []
for i in range(panels + 1):
    start = bottom_joints[i]
    end = top_joints[i]
    name = f"Vertical_{i}"
    vert = create_member(name, start, end, web_section[:2], False)
    verticals.append(vert)

# Create diagonal members (10 members, alternating)
diagonals = []
# Left half (5 diagonals sloping up-right)
for i in range(panels//2):
    start = bottom_joints[i]
    end = top_joints[i+1]
    name = f"Diagonal_L_{i}"
    diag = create_member(name, start, end, web_section[:2], False)
    diagonals.append(diag)
# Right half (5 diagonals sloping up-left)
for i in range(panels//2, panels):
    start = top_joints[i]
    end = bottom_joints[i+1]
    name = f"Diagonal_R_{i}"
    diag = create_member(name, start, end, web_section[:2], False)
    diagonals.append(diag)

# Create fixed constraints at joints
all_members = bottom_chords + top_chords + verticals + diagonals
joint_objects = {}

# Group objects by joint location
for obj in all_members:
    # Get approximate joint locations from object ends
    # For simplicity, use object location as joint (midpoint for chords/diagonals)
    loc_key = (round(obj.location.x, 3), round(obj.location.z, 3))
    if loc_key not in joint_objects:
        joint_objects[loc_key] = []
    joint_objects[loc_key].append(obj)

# Create constraints for each joint (connect first object to all others)
constraints = []
for loc, objects in joint_objects.items():
    if len(objects) > 1:
        base_obj = objects[0]
        for other_obj in objects[1:]:
            if base_obj != other_obj:
                constraint = create_fixed_constraint(base_obj, other_obj)
                constraints.append(constraint)

# Apply distributed load to top chords
for i, chord in enumerate(top_chords):
    # Add constant force downward
    chord.rigid_body.use_gravity = True
    # Additional force to simulate load
    # In Blender, we can't directly add force in headless without simulation
    # We'll increase mass to simulate load effect
    chord.rigid_body.mass += load_per_panel / 9.81  # Convert to mass equivalent

# Set world gravity
bpy.context.scene.gravity = (0, 0, -9.81)

# Enable rigid body world
bpy.context.scene.rigidbody_world.enabled = True

print(f"Howe truss constructed with {len(bottom_chords)} bottom chords, {len(top_chords)} top chords,")
print(f"{len(verticals)} verticals, {len(diagonals)} diagonals, and {len(constraints)} fixed constraints.")
print(f"Total load: {total_load}N distributed across {panels} panels ({load_per_panel}N per panel).")