import bpy
import math
from mathutils import Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
span_length = 7.0
top_chord_z = 2.0
bottom_chord_z = 1.0
chord_dims = (7.0, 0.2, 0.2)
vertical_count = 5
vertical_spacing = 1.75
vertical_dims = (0.2, 0.2, 1.0)
vertical_center_z = 1.5
diagonal_length = 2.015564
diagonal_angle = math.radians(29.74488)
diagonal_dims = (0.2, 0.2, diagonal_length)
attachment_dims = (0.5, 0.5, 0.5)
attachment_loc = (3.5, 0.0, 2.35)
force_magnitude = 2943.0
foundation_size = (0.5, 0.5, 0.5)
foundation_locs = [(0.0, 0.0, 0.25), (7.0, 0.0, 0.25)]
simulation_frames = 100
solver_iterations = 60

# Set up rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.frame_end = simulation_frames

# Helper to add rigid body
def add_rigidbody(obj, body_type='ACTIVE', collision_shape='BOX'):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.collision_shape = collision_shape
    obj.rigid_body.collision_margin = 0.0
    obj.rigid_body.mass = 1.0  # Auto mass based on volume

# Helper to create a cube with given dimensions and location
def create_cube(name, dims, loc):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dims[0]/2, dims[1]/2, dims[2]/2)  # Cube default size 2, so half for scaling
    return obj

# Create foundations (passive)
foundations = []
for i, loc in enumerate(foundation_locs):
    f = create_cube(f"Foundation_{i}", foundation_size, loc)
    add_rigidbody(f, 'PASSIVE')
    foundations.append(f)

# Create chords
top_chord = create_cube("TopChord", chord_dims, (span_length/2, 0, top_chord_z))
add_rigidbody(top_chord)
bottom_chord = create_cube("BottomChord", chord_dims, (span_length/2, 0, bottom_chord_z))
add_rigidbody(bottom_chord)

# Create vertical members
verticals = []
for i in range(vertical_count):
    x = i * vertical_spacing
    v = create_cube(f"Vertical_{i}", vertical_dims, (x, 0, vertical_center_z))
    add_rigidbody(v)
    verticals.append(v)

# Create diagonal members (alternating direction)
diagonals = []
for i in range(vertical_count - 1):
    x_mid = (i * vertical_spacing) + (vertical_spacing / 2)
    z_mid = (top_chord_z + bottom_chord_z) / 2
    # Alternate direction: first bay diagonal from top-left to bottom-right
    if i % 2 == 0:
        angle = diagonal_angle
    else:
        angle = -diagonal_angle
    d = create_cube(f"Diagonal_{i}", diagonal_dims, (x_mid, 0, z_mid))
    # Rotate around Y-axis
    d.rotation_euler = (0, angle, 0)
    add_rigidbody(d)
    diagonals.append(d)

# Create signal attachment
attachment = create_cube("SignalAttachment", attachment_dims, attachment_loc)
add_rigidbody(attachment)
# Apply downward force
attachment.rigid_body.constant_force = (0, 0, -force_magnitude)

# Add fixed constraints between all connecting members
# We'll connect each joint: for each vertical, connect to top and bottom chords.
# For diagonals, connect to top chord at one end and bottom chord at other.
# Also connect attachment to top chord at center.
# Use Blender's rigid body constraint empties.
def add_fixed_constraint(obj1, obj2):
    # Create empty as constraint holder
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=((obj1.location + obj2.location) * 0.5))
    empty = bpy.context.active_object
    empty.empty_display_size = 0.2
    # Add rigid body constraint component
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj1
    empty.rigid_body_constraint.object2 = obj2

# Connect verticals to chords
for i, v in enumerate(verticals):
    add_fixed_constraint(v, top_chord)
    add_fixed_constraint(v, bottom_chord)

# Connect diagonals
for i, d in enumerate(diagonals):
    # Determine which vertical indices it connects
    if i % 2 == 0:
        # Connects top at x=i*spacing to bottom at (i+1)*spacing
        top_point = i * vertical_spacing
        bottom_point = (i + 1) * vertical_spacing
    else:
        # Connects bottom at x=i*spacing to top at (i+1)*spacing
        top_point = (i + 1) * vertical_spacing
        bottom_point = i * vertical_spacing
    # We'll approximate by connecting to chords directly (since chords are continuous)
    add_fixed_constraint(d, top_chord)
    add_fixed_constraint(d, bottom_chord)

# Connect attachment to top chord
add_fixed_constraint(attachment, top_chord)

# Connect bottom chord ends to foundations
add_fixed_constraint(bottom_chord, foundations[0])
add_fixed_constraint(bottom_chord, foundations[1])

# Ensure all objects have proper collision bounds
for obj in bpy.data.objects:
    if obj.rigid_body is not None:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.0

print("Pratt truss gantry construction complete. Simulate for 100 frames.")