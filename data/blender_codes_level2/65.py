import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
span = 8.0
top_z = 2.0
bottom_z = 0.5
chord_cs = 0.3
vert_count = 5
bay = 2.0
vert_dim = (0.3, 0.3, 1.5)
diag_len = 2.5
diag_cs = 0.3
load_mass = 700.0
load_size = 0.5
load_x = 4.0
load_z = 2.25

# Create top chord (horizontal beam at Z=2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(span/2, 0, top_z))
top_chord = bpy.context.active_object
top_chord.name = "Top_Chord"
top_chord.scale = (span, chord_cs, chord_cs)
bpy.ops.rigidbody.object_add()
top_chord.rigid_body.type = 'PASSIVE'

# Create bottom chord (horizontal beam at Z=0.5)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(span/2, 0, bottom_z))
bottom_chord = bpy.context.active_object
bottom_chord.name = "Bottom_Chord"
bottom_chord.scale = (span, chord_cs, chord_cs)
bpy.ops.rigidbody.object_add()
bottom_chord.rigid_body.type = 'PASSIVE'

# Create vertical members at X = 0, 2, 4, 6, 8
vertical_members = []
for i in range(vert_count):
    x_pos = i * bay
    # Vertical center: midway between chord centers (Z=1.25)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0, 1.25))
    vert = bpy.context.active_object
    vert.name = f"Vertical_{i}"
    vert.scale = vert_dim
    bpy.ops.rigidbody.object_add()
    vert.rigid_body.type = 'PASSIVE'
    vertical_members.append(vert)

# Create diagonal members in Pratt pattern
diagonal_members = []
for i in range(vert_count - 1):
    # Alternating pattern: bay 0-2: bottom(0) to top(2), bay 2-4: top(2) to bottom(4), etc.
    if i % 2 == 0:  # Even bays: bottom-left to top-right
        start_x = i * bay
        start_z = bottom_z
        end_x = (i + 1) * bay
        end_z = top_z
    else:  # Odd bays: top-left to bottom-right
        start_x = i * bay
        start_z = top_z
        end_x = (i + 1) * bay
        end_z = bottom_z
    
    # Diagonal center position
    center_x = (start_x + end_x) / 2
    center_z = (start_z + end_z) / 2
    
    # Create diagonal beam
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, 0, center_z))
    diag = bpy.context.active_object
    diag.name = f"Diagonal_{i}"
    
    # Scale: length along X, cross-section in Y/Z
    diag.scale = (diag_len, diag_cs, diag_cs)
    
    # Calculate rotation angle (around Y-axis)
    dx = end_x - start_x
    dz = end_z - start_z
    angle = math.atan2(dz, dx)  # Positive for upward slope
    
    # Apply rotation
    diag.rotation_euler = (0, angle, 0)
    
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'PASSIVE'
    diagonal_members.append(diag)

# Create load cube at center
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(load_x, 0, load_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Create FIXED constraints between all connected members
# We'll create constraints for each joint location
joints = []

# Vertical-to-chord joints
for i, vert in enumerate(vertical_members):
    x_pos = i * bay
    
    # Top joint (connects vertical, top chord, possibly diagonals)
    joints.append({
        'location': (x_pos, 0, top_z),
        'objects': [vert, top_chord]
    })
    
    # Bottom joint (connects vertical, bottom chord, possibly diagonals)
    joints.append({
        'location': (x_pos, 0, bottom_z),
        'objects': [vert, bottom_chord]
    })

# Diagonal-to-chord joints (already included in some vertical joints, add missing ones)
for i, diag in enumerate(diagonal_members):
    if i % 2 == 0:  # Even: bottom-left to top-right
        joints.append({
            'location': (i * bay, 0, bottom_z),
            'objects': [diag, bottom_chord]
        })
        joints.append({
            'location': ((i + 1) * bay, 0, top_z),
            'objects': [diag, top_chord]
        })
    else:  # Odd: top-left to bottom-right
        joints.append({
            'location': (i * bay, 0, top_z),
            'objects': [diag, top_chord]
        })
        joints.append({
            'location': ((i + 1) * bay, 0, bottom_z),
            'objects': [diag, bottom_chord]
        })

# Create constraint objects for each unique joint
# In headless mode, we must carefully manage object selection
created_constraints = []
for joint in joints:
    # Create empty at joint location for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint['location'])
    empty = bpy.context.active_object
    empty.name = "Constraint_Empty"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = "Fixed_Constraint"
    constraint.rigid_body_constraint.type = 'FIXED'
    
    # Parent constraint to empty
    constraint.parent = empty
    
    # Set connected objects
    # In headless mode, we set the constraint properties directly
    if len(joint['objects']) >= 2:
        constraint.rigid_body_constraint.object1 = joint['objects'][0]
        constraint.rigid_body_constraint.object2 = joint['objects'][1]
    
    created_constraints.append((empty, constraint))

# Set up physics world if not already configured
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Adjust gravity if needed (standard Earth gravity)
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)

print("Pratt Truss structure created with fixed constraints and 700kg load.")