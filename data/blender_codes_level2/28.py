import bpy
import math
from mathutils import Vector, Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
span_length = 6.0
top_chord_z = 3.0
bottom_chord_z = 2.0
chord_cross_section = 0.15
vertical_height = 1.0
vertical_cross_section = 0.1
diagonal_length = 2.23606797749979
diagonal_cross_section = 0.1
pipe_radius = 0.2
pipe_length = 6.0
pipe_z = 1.5
vertical_x_positions = [-3.0, -1.0, 1.0, 3.0]
diagonal_pairs = [
    ((-3.0, top_chord_z), (-1.0, bottom_chord_z)),
    ((-1.0, top_chord_z), (1.0, bottom_chord_z)),
    ((-1.0, bottom_chord_z), (1.0, top_chord_z)),
    ((1.0, bottom_chord_z), (3.0, top_chord_z))
]
pipe_attachment_x = [-1.0, 1.0]
pipe_mass_kg = 400.0
gravity = 9.81
total_force_N = pipe_mass_kg * gravity

# Set up physics world
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Function to create rigid body
def add_rigidbody(obj, body_type='PASSIVE', mass=1.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    if body_type == 'ACTIVE':
        obj.rigid_body.mass = mass
        obj.rigid_body.collision_shape = 'MESH'

# 1. Create Top Chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, top_chord_z))
top_chord = bpy.context.active_object
top_chord.scale = (span_length, chord_cross_section, chord_cross_section)
top_chord.name = "Top_Chord"
add_rigidbody(top_chord, 'PASSIVE')

# 2. Create Bottom Chord
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, bottom_chord_z))
bottom_chord = bpy.context.active_object
bottom_chord.scale = (span_length, chord_cross_section, chord_cross_section)
bottom_chord.name = "Bottom_Chord"
add_rigidbody(bottom_chord, 'PASSIVE')

# 3. Create Vertical Members
vertical_objects = []
for i, x_pos in enumerate(vertical_x_positions):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0, 2.5))  # Center between top and bottom
    vert = bpy.context.active_object
    vert.scale = (vertical_cross_section, vertical_cross_section, vertical_height)
    vert.name = f"Vertical_{i+1}"
    add_rigidbody(vert, 'PASSIVE')
    vertical_objects.append(vert)

# 4. Create Diagonal Members
diagonal_objects = []
for i, (start, end) in enumerate(diagonal_pairs):
    # Calculate center position
    center_x = (start[0] + end[0]) / 2
    center_z = (start[1] + end[1]) / 2
    
    # Calculate rotation
    dx = end[0] - start[0]
    dz = end[1] - start[1]
    length_2d = math.sqrt(dx**2 + dz**2)
    
    # Create diagonal cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, 0, center_z))
    diag = bpy.context.active_object
    diag.scale = (diagonal_length, diagonal_cross_section, diagonal_cross_section)
    diag.name = f"Diagonal_{i+1}"
    
    # Rotate to align with diagonal direction
    angle = math.atan2(dz, dx)
    diag.rotation_euler = Euler((0, 0, -angle), 'XYZ')
    
    add_rigidbody(diag, 'PASSIVE')
    diagonal_objects.append(diag)

# 5. Create Pipe
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=pipe_radius,
    depth=pipe_length,
    location=(0, 0, pipe_z)
)
pipe = bpy.context.active_object
pipe.name = "Pipe"
pipe.rotation_euler = Euler((0, 0, 0), 'XYZ')  # Already aligned along Y axis
add_rigidbody(pipe, 'ACTIVE', pipe_mass_kg)

# 6. Create Fixed Constraints between structural members
def create_fixed_constraint(obj1, obj2, location):
    # Create empty at connection point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    
    # Parent constraint to empty for organization
    constraint.parent = empty

# Connect verticals to top and bottom chords
for vert_obj, x_pos in zip(vertical_objects, vertical_x_positions):
    # Top connection
    create_fixed_constraint(vert_obj, top_chord, (x_pos, 0, top_chord_z))
    # Bottom connection
    create_fixed_constraint(vert_obj, bottom_chord, (x_pos, 0, bottom_chord_z))

# Connect diagonals to chords
for i, diag_obj in enumerate(diagonal_objects):
    start, end = diagonal_pairs[i]
    # Start point connection
    start_obj = top_chord if start[1] == top_chord_z else bottom_chord
    create_fixed_constraint(diag_obj, start_obj, (start[0], 0, start[1]))
    # End point connection
    end_obj = top_chord if end[1] == top_chord_z else bottom_chord
    create_fixed_constraint(diag_obj, end_obj, (end[0], 0, end[1]))

# Connect pipe to bottom chord at attachment points
for x_pos in pipe_attachment_x:
    create_fixed_constraint(pipe, bottom_chord, (x_pos, 0, pipe_z))

# Set simulation frame range
bpy.context.scene.frame_end = 100

# Optional: Set viewport display for better visualization
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.show_wire = True
        obj.show_all_edges = True

print("Pratt truss pipe support structure created successfully.")
print(f"Total downward force on pipe: {total_force_N:.1f} N ({pipe_mass_kg} kg)")