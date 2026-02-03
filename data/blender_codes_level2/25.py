import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
span_length = 8.0
top_chord_z = 2.0
bottom_chord_z = 0.0
chord_y = 0.0
chord_cross_section = 0.2
vertical_positions = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
vertical_cross_section = 0.1
vertical_height = 2.0
diagonal_x_pairs = [(-4.0, -3.0), (-3.0, -2.0), (-2.0, -1.0), (-1.0, 0.0), 
                    (0.0, 1.0), (1.0, 2.0), (2.0, 3.0), (3.0, 4.0)]
diagonal_cross_section = 0.1
diagonal_length = math.sqrt(1.0**2 + 2.0**2)
load_mass_kg = 500
load_position = (0.0, 0.0, 2.0)
simulation_frames = 100

# Helper: Create cube with rigid body
def create_cube(name, location, scale, rigid_body_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    return obj

# Helper: Create FIXED constraint between two objects
def create_fixed_constraint(obj1, obj2):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# 1. Create top chord (horizontal beam)
top_chord = create_cube(
    "TopChord",
    location=(0.0, chord_y, top_chord_z),
    scale=(span_length, chord_cross_section, chord_cross_section)
)

# 2. Create bottom chord (horizontal beam)
bottom_chord = create_cube(
    "BottomChord",
    location=(0.0, chord_y, bottom_chord_z),
    scale=(span_length, chord_cross_section, chord_cross_section)
)

# 3. Create vertical members
vertical_objects = []
for i, x_pos in enumerate(vertical_positions):
    # Vertical center is midway between top and bottom chords
    z_center = (top_chord_z + bottom_chord_z) / 2
    vert = create_cube(
        f"Vertical_{i}",
        location=(x_pos, chord_y, z_center),
        scale=(vertical_cross_section, vertical_cross_section, vertical_height)
    )
    vertical_objects.append(vert)
    # Constrain to top chord
    create_fixed_constraint(vert, top_chord)
    # Constrain to bottom chord
    create_fixed_constraint(vert, bottom_chord)

# 4. Create diagonal members
for i, (x_start, x_end) in enumerate(diagonal_x_pairs):
    # Determine start and end Z based on alternating pattern
    if i % 2 == 0:  # Top -> Bottom
        z_start, z_end = top_chord_z, bottom_chord_z
    else:           # Bottom -> Top
        z_start, z_end = bottom_chord_z, top_chord_z
    
    # Calculate midpoint and rotation
    mid_x = (x_start + x_end) / 2
    mid_z = (z_start + z_end) / 2
    dx = x_end - x_start
    dz = z_end - z_start
    angle = math.atan2(dz, dx)  # Rotation around Y-axis
    
    # Create diagonal cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mid_x, chord_y, mid_z))
    diag = bpy.context.active_object
    diag.name = f"Diagonal_{i}"
    # Scale: length in X, cross-section in Y and Z
    diag.scale = (diagonal_length/2, diagonal_cross_section/2, diagonal_cross_section/2)
    bpy.ops.object.transform_apply(scale=True)
    # Rotate to align with diagonal direction
    diag.rotation_euler = (0.0, angle, 0.0)
    bpy.ops.object.transform_apply(rotation=True)
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'PASSIVE'
    
    # Create constraints at both ends
    # Find endpoint objects (chords)
    start_chord = top_chord if z_start == top_chord_z else bottom_chord
    end_chord = top_chord if z_end == top_chord_z else bottom_chord
    create_fixed_constraint(diag, start_chord)
    create_fixed_constraint(diag, end_chord)

# 5. Create load (500 kg mass)
bpy.ops.mesh.primitive_cube_add(size=0.3, location=load_position)
load = bpy.context.active_object
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass_kg
# Position slightly above top chord for contact
load.location.z += 0.15

# 6. Configure physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

print(f"Pratt truss bridge constructed. Simulating {simulation_frames} frames with {load_mass_kg}kg load.")