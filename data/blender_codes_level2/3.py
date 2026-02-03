import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
span_length = 8.0
top_chord_z = 3.0
bottom_chord_z = 1.5
y_center = 0.0
chord_width = 0.2
chord_height = 0.2
web_width = 0.15
web_height = 0.15
node_x = [-4.0, -2.0, 0.0, 2.0, 4.0]
load_force_newton = 9806.65
simulation_frames = 100

# Function to create a rectangular beam member
def create_beam(name, location, rotation, scale):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = scale
    # Apply rotation (in radians)
    beam.rotation_euler = rotation
    # Apply scale and rotation to mesh
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.collision_margin = 0.0
    return beam

# Create top chord (horizontal beam)
top_chord = create_beam(
    name="TopChord",
    location=(0.0, y_center, top_chord_z),
    rotation=(0.0, 0.0, 0.0),
    scale=(span_length, chord_width, chord_height)
)
top_chord.rigid_body.type = 'ACTIVE'

# Create bottom chord
bottom_chord = create_beam(
    name="BottomChord",
    location=(0.0, y_center, bottom_chord_z),
    rotation=(0.0, 0.0, 0.0),
    scale=(span_length, chord_width, chord_height)
)
bottom_chord.rigid_body.type = 'ACTIVE'

# Create vertical members
vertical_members = []
for i, x in enumerate(node_x):
    v_name = f"Vertical_{i}"
    v_z_center = (top_chord_z + bottom_chord_z) / 2.0
    v_height = top_chord_z - bottom_chord_z
    vertical = create_beam(
        name=v_name,
        location=(x, y_center, v_z_center),
        rotation=(0.0, 0.0, 0.0),
        scale=(web_width, web_height, v_height)
    )
    vertical.rigid_body.type = 'ACTIVE'
    vertical_members.append(vertical)

# Create diagonal members
diagonal_members = []
diagonal_pairs = [
    (-4.0, bottom_chord_z, -2.0, top_chord_z),
    (-4.0, top_chord_z, -2.0, bottom_chord_z),
    (2.0, bottom_chord_z, 4.0, top_chord_z),
    (2.0, top_chord_z, 4.0, bottom_chord_z)
]
for i, (x1, z1, x2, z2) in enumerate(diagonal_pairs):
    d_name = f"Diagonal_{i}"
    # Midpoint
    mid_x = (x1 + x2) / 2.0
    mid_z = (z1 + z2) / 2.0
    # Length and orientation
    dx = x2 - x1
    dz = z2 - z1
    length = math.sqrt(dx*dx + dz*dz)
    angle = math.atan2(dz, dx)
    # Create diagonal
    diagonal = create_beam(
        name=d_name,
        location=(mid_x, y_center, mid_z),
        rotation=(0.0, -angle, 0.0),  # Rotate around Y axis
        scale=(length, web_width, web_height)
    )
    diagonal.rigid_body.type = 'ACTIVE'
    diagonal_members.append(diagonal)

# Create fixed constraints at joints
def add_fixed_constraint(obj_a, obj_b):
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_a.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Connect joints (simplified: connect adjacent members at node positions)
# For each node X, connect intersecting members
for i, x in enumerate(node_x):
    # Collect members meeting at this X coordinate
    members_at_node = []
    
    # Check top chord (all nodes along top)
    if abs(x) <= 4.0:
        members_at_node.append(top_chord)
    
    # Check bottom chord
    if abs(x) <= 4.0:
        members_at_node.append(bottom_chord)
    
    # Check vertical at this X
    members_at_node.append(vertical_members[i])
    
    # Check diagonals
    for diag in diagonal_members:
        # Get diagonal endpoints from its transform
        diag_loc = diag.location
        diag_length = diag.scale.x
        diag_angle = diag.rotation_euler.y
        # Calculate endpoints in world coordinates
        cos_a = math.cos(-diag_angle)
        sin_a = math.sin(-diag_angle)
        end1_x = diag_loc.x - diag_length/2 * cos_a
        end1_z = diag_loc.z - diag_length/2 * sin_a
        end2_x = diag_loc.x + diag_length/2 * cos_a
        end2_z = diag_loc.z + diag_length/2 * sin_a
        # Check if this node matches either endpoint
        if (abs(end1_x - x) < 0.01 and abs(end1_z - top_chord_z) < 0.01) or 
           (abs(end1_x - x) < 0.01 and abs(end1_z - bottom_chord_z) < 0.01) or 
           (abs(end2_x - x) < 0.01 and abs(end2_z - top_chord_z) < 0.01) or 
           (abs(end2_x - x) < 0.01 and abs(end2_z - bottom_chord_z) < 0.01):
            members_at_node.append(diag)
    
    # Create fixed constraints between all pairs at this joint
    for j in range(len(members_at_node)):
        for k in range(j+1, len(members_at_node)):
            add_fixed_constraint(members_at_node[j], members_at_node[k])

# Create foundation supports (passive rigid bodies at ends)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.0, y_center, bottom_chord_z - 0.5))
left_support = bpy.context.active_object
left_support.name = "LeftSupport"
left_support.scale = (0.5, 0.5, 0.5)
bpy.ops.rigidbody.object_add()
left_support.rigid_body.type = 'PASSIVE'

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(4.0, y_center, bottom_chord_z - 0.5))
right_support = bpy.context.active_object
right_support.name = "RightSupport"
right_support.scale = (0.5, 0.5, 0.5)
bpy.ops.rigidbody.object_add()
right_support.rigid_body.type = 'PASSIVE'

# Connect bottom chord ends to supports
add_fixed_constraint(bottom_chord, left_support)
add_fixed_constraint(bottom_chord, right_support)

# Apply downward force at top chord center
# We'll use a force field for simplicity in headless mode
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, y_center, top_chord_z))
force_empty = bpy.context.active_object
force_empty.name = "LoadPoint"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = -load_force_newton  # Negative Z direction
force_empty.field.use_max_distance = True
force_empty.field.distance_max = 0.5  # Only affect nearby objects

# Set up simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Enable gravity (default is -9.81 Z)
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

print("Howe Truss construction complete. Run simulation for", simulation_frames, "frames.")