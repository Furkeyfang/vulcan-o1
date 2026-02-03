import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_length = 4.0
top_chord_z = 0.6
bottom_chord_z = 0.1
chord_width = 0.1
chord_height = 0.1
vertical_height = 0.5
vertical_width = 0.1
vertical_locations = [0.0, 1.0, 2.0, 3.0, 4.0]
diagonal_true_length = 1.118033988749895
diagonal_width = 0.1
diagonal_height = 0.1
diagonal_pairs = [
    ((0.0, 0.0, top_chord_z - chord_height/2), (1.0, 0.0, bottom_chord_z + chord_height/2)),
    ((1.0, 0.0, bottom_chord_z + chord_height/2), (2.0, 0.0, top_chord_z - chord_height/2)),
    ((2.0, 0.0, top_chord_z - chord_height/2), (3.0, 0.0, bottom_chord_z + chord_height/2)),
    ((3.0, 0.0, bottom_chord_z + chord_height/2), (4.0, 0.0, top_chord_z - chord_height/2))
]
load_mass_kg = 500.0
load_size = 0.5
load_center_x = 2.0
load_center_z = 1.35
support_locations = [(0.0, 0.0, bottom_chord_z), (4.0, 0.0, bottom_chord_z)]

# Helper to create cube with rigid body
def create_cube(name, location, scale, rigid_type='ACTIVE', mass=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Create top chord (single piece)
create_cube(
    "TopChord",
    (span_length/2, 0.0, top_chord_z),
    (span_length, chord_width, chord_height),
    'ACTIVE',
    mass=span_length * chord_width * chord_height * 7850  # steel density
)

# Create bottom chord
create_cube(
    "BottomChord",
    (span_length/2, 0.0, bottom_chord_z),
    (span_length, chord_width, chord_height),
    'ACTIVE',
    mass=span_length * chord_width * chord_height * 7850
)

# Create vertical members
vertical_objs = []
for i, x in enumerate(vertical_locations):
    obj = create_cube(
        f"Vertical_{i}",
        (x, 0.0, bottom_chord_z + vertical_height/2),
        (vertical_width, vertical_width, vertical_height),
        'ACTIVE',
        mass=vertical_width * vertical_width * vertical_height * 7850
    )
    vertical_objs.append(obj)

# Create diagonal members
diagonal_objs = []
for i, (start, end) in enumerate(diagonal_pairs):
    start_vec = Vector(start)
    end_vec = Vector(end)
    center = (start_vec + end_vec) / 2
    length = (end_vec - start_vec).length
    direction = (end_vec - start_vec).normalized()
    
    # Create cube and scale to match true length
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.active_object
    obj.name = f"Diagonal_{i}"
    # Scale: X along member length, Y/Z for cross-section
    obj.scale = (length/2, diagonal_width/2, diagonal_height/2)  # cube size 2, so half length
    # Rotate to align with direction
    rot_quat = Vector((1,0,0)).rotation_difference(direction).to_matrix().to_4x4()
    obj.matrix_world = Matrix.Translation(center) @ rot_quat.to_4x4() @ Matrix.Scale(1,4, (1,0,0))
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.mass = length * diagonal_width * diagonal_height * 7850
    obj.rigid_body.collision_shape = 'BOX'
    diagonal_objs.append(obj)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(load_center_x, 0.0, load_center_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size/2, load_size/2, load_size/2)  # cube size 2, so half
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass_kg
load.rigid_body.collision_shape = 'BOX'

# Create fixed supports (passive rigid bodies)
support_objs = []
for i, loc in enumerate(support_locations):
    obj = create_cube(
        f"Support_{i}",
        loc,
        (0.2, 0.2, 0.1),
        'PASSIVE',
        mass=0.0
    )
    support_objs.append(obj)

# Create fixed constraints between members at joints
# Collect objects by proximity (simplified: hardcode connections)
joints = {
    (0.0, 0.0, top_chord_z): ["TopChord", "Vertical_0", "Diagonal_0"],
    (1.0, 0.0, top_chord_z): ["TopChord", "Vertical_1"],
    (2.0, 0.0, top_chord_z): ["TopChord", "Vertical_2", "Diagonal_1", "Diagonal_2"],
    (3.0, 0.0, top_chord_z): ["TopChord", "Vertical_3"],
    (4.0, 0.0, top_chord_z): ["TopChord", "Vertical_4", "Diagonal_3"],
    (0.0, 0.0, bottom_chord_z): ["BottomChord", "Vertical_0", "Support_0"],
    (1.0, 0.0, bottom_chord_z): ["BottomChord", "Vertical_1", "Diagonal_0", "Diagonal_1"],
    (2.0, 0.0, bottom_chord_z): ["BottomChord", "Vertical_2"],
    (3.0, 0.0, bottom_chord_z): ["BottomChord", "Vertical_3", "Diagonal_2", "Diagonal_3"],
    (4.0, 0.0, bottom_chord_z): ["BottomChord", "Vertical_4", "Support_1"],
}

for joint_loc, obj_names in joints.items():
    objects = [bpy.data.objects[name] for name in obj_names if name in bpy.data.objects]
    if len(objects) < 2:
        continue
    # Create fixed constraint between first object and each of the others
    base = objects[0]
    for other in objects[1:]:
        # Create constraint empty
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=joint_loc)
        empty = bpy.context.active_object
        empty.name = f"Fixed_{base.name}_{other.name}"
        bpy.ops.rigidbody.constraint_add()
        empty.rigid_body_constraint.type = 'FIXED'
        empty.rigid_body_constraint.object1 = base
        empty.rigid_body_constraint.object2 = other

# Set rigid body world settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Run simulation for 100 frames
bpy.context.scene.frame_end = 100