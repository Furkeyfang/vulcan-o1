import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
span_length = 5.0
truss_height = 1.25
member_cross_section = 0.1
truss_separation_y = 1.0
truss_a_y = -0.5
truss_b_y = 0.5
diagonal_length = math.sqrt((span_length/2)**2 + truss_height**2)  # 2.795085
cross_member_spacing = 0.5
cross_member_x_positions = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
load_mass_kg = 400.0
load_cube_size = (1.0, 1.0, 0.5)
load_cube_location = (0.0, 0.0, 1.55)
bottom_chord_z = 0.0
top_chord_z = 1.25

# Helper function to create a cuboid member
def create_member(name, location, scale, rotation_euler=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation_euler
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    return obj

# Helper function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b):
    # Create empty object as constraint center
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=((obj_a.location.x + obj_b.location.x)/2,
                                                          (obj_a.location.y + obj_b.location.y)/2,
                                                          (obj_a.location.z + obj_b.location.z)/2))
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Create truss A (Y = -0.5)
# Bottom chord A
bottom_chord_a = create_member("BottomChord_A", (0, truss_a_y, bottom_chord_z),
                               (span_length, member_cross_section, member_cross_section))
# Top chord A
top_chord_a = create_member("TopChord_A", (0, truss_a_y, top_chord_z),
                            (span_length, member_cross_section, member_cross_section))
# Diagonal A1 (left)
diag_a1_angle = math.atan2(truss_height, span_length/2)
diag_a1_loc = (-span_length/4, truss_a_y, truss_height/2)
diag_a1 = create_member("Diag_A1", diag_a1_loc,
                        (diagonal_length, member_cross_section, member_cross_section),
                        (0, 0, -diag_a1_angle))
# Diagonal A2 (right)
diag_a2_angle = math.atan2(truss_height, -span_length/2)
diag_a2_loc = (span_length/4, truss_a_y, truss_height/2)
diag_a2 = create_member("Diag_A2", diag_a2_loc,
                        (diagonal_length, member_cross_section, member_cross_section),
                        (0, 0, -diag_a2_angle))

# Create truss B (Y = 0.5) by duplicating truss A and translating
truss_objects_a = [bottom_chord_a, top_chord_a, diag_a1, diag_a2]
truss_objects_b = []
for obj in truss_objects_a:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value": (0, truss_separation_y, 0)})
    dup = bpy.context.active_object
    dup.name = obj.name.replace("_A", "_B")
    truss_objects_b.append(dup)

# Assign truss B objects to variables for constraint creation
bottom_chord_b = truss_objects_b[0]
top_chord_b = truss_objects_b[1]
diag_b1 = truss_objects_b[2]
diag_b2 = truss_objects_b[3]

# Create cross-members at bottom (Z=0)
bottom_cross_members = []
for x in cross_member_x_positions:
    name = f"BottomCross_X{x}"
    loc = (x, 0, bottom_chord_z)
    scale = (member_cross_section, truss_separation_y, member_cross_section)
    obj = create_member(name, loc, scale)
    bottom_cross_members.append(obj)

# Create cross-members at top (Z=1.25)
top_cross_members = []
for x in cross_member_x_positions:
    name = f"TopCross_X{x}"
    loc = (x, 0, top_chord_z)
    scale = (member_cross_section, truss_separation_y, member_cross_section)
    obj = create_member(name, loc, scale)
    top_cross_members.append(obj)

# Create fixed constraints for truss A joints
# Left joint: bottom chord A, diagonal A1, and bottom cross at X=-2.0 (closest)
create_fixed_constraint(bottom_chord_a, diag_a1)
# Right joint: bottom chord A, diagonal A2, and bottom cross at X=2.0
create_fixed_constraint(bottom_chord_a, diag_a2)
# Apex joint: top chord A, diagonal A1, diagonal A2, and top cross at X=0.0
create_fixed_constraint(top_chord_a, diag_a1)
create_fixed_constraint(top_chord_a, diag_a2)

# Repeat for truss B
create_fixed_constraint(bottom_chord_b, diag_b1)
create_fixed_constraint(bottom_chord_b, diag_b2)
create_fixed_constraint(top_chord_b, diag_b1)
create_fixed_constraint(top_chord_b, diag_b2)

# Connect cross-members to chords
for i, x in enumerate(cross_member_x_positions):
    # Bottom cross to bottom chords
    create_fixed_constraint(bottom_cross_members[i], bottom_chord_a)
    create_fixed_constraint(bottom_cross_members[i], bottom_chord_b)
    # Top cross to top chords
    create_fixed_constraint(top_cross_members[i], top_chord_a)
    create_fixed_constraint(top_cross_members[i], top_chord_b)

# Connect corresponding cross-members at same X (optional, for redundancy)
for i in range(len(cross_member_x_positions)):
    create_fixed_constraint(bottom_cross_members[i], top_cross_members[i])

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=load_cube_location)
load_cube = bpy.context.active_object
load_cube.name = "LoadCube"
load_cube.scale = load_cube_size
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass_kg

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100  # Simulate 100 frames