import bpy
import math
from mathutils import Matrix, Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_half = 4.5
bottom_z = 0.5
bottom_y_offset = 0.1
bottom_length = 9.0
bottom_width = 0.2
bottom_height = 0.3
top_z = 2.0
top_length = 9.0
top_width = 0.2
top_height = 0.3
vertical_h = 1.5
vertical_w = 0.2
vertical_d = 0.2
diagonal_l = 2.121
diagonal_angle = math.radians(45.0)
diagonal_w = 0.2
diagonal_d = 0.2
load_force = 6376.5

# Function to create beam with physics
def create_beam(name, location, scale, rotation=(0,0,0), rigid_type='ACTIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = scale
    if any(rotation):
        beam.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = rigid_type
    beam.rigid_body.collision_shape = 'BOX'
    return beam

# Create bottom chords (passive - fixed supports)
bottom1 = create_beam(
    "BottomChord_Left",
    location=(0.0, -bottom_y_offset, bottom_z),
    scale=(bottom_length, bottom_width, bottom_height),
    rigid_type='PASSIVE'
)
bottom2 = create_beam(
    "BottomChord_Right", 
    location=(0.0, bottom_y_offset, bottom_z),
    scale=(bottom_length, bottom_width, bottom_height),
    rigid_type='PASSIVE'
)

# Create top chord (active - carries load)
top = create_beam(
    "TopChord",
    location=(0.0, 0.0, top_z),
    scale=(top_length, top_width, top_height),
    rigid_type='ACTIVE'
)

# Create vertical members (active)
vert_positions = [(-span_half, 0.0), (0.0, 0.0), (span_half, 0.0)]
verticals = []
for i, (x, y) in enumerate(vert_positions):
    vert = create_beam(
        f"Vertical_{i}",
        location=(x, y, bottom_z + vertical_h/2),
        scale=(vertical_w, vertical_d, vertical_h),
        rigid_type='ACTIVE'
    )
    verticals.append(vert)

# Create diagonal members (active, 45° orientation)
# Left side diagonals (two per side, mirrored for right side)
diag_data = [
    # Left top to left middle bottom
    {"name": "Diagonal_L1", "start_x": -span_half, "end_x": -span_half + 1.5, "y_sign": -1},
    # Left middle top to left center bottom  
    {"name": "Diagonal_L2", "start_x": -span_half + 1.5, "end_x": -span_half + 3.0, "y_sign": -1},
    # Right middle top to right center bottom
    {"name": "Diagonal_R1", "start_x": span_half - 1.5, "end_x": span_half - 3.0, "y_sign": 1},
    # Right top to right middle bottom
    {"name": "Diagonal_R2", "start_x": span_half, "end_x": span_half - 1.5, "y_sign": 1}
]

diagonals = []
for data in diag_data:
    # Calculate midpoint and rotation
    start = Vector((data["start_x"], data["y_sign"]*bottom_y_offset, top_z))
    end = Vector((data["end_x"], data["y_sign"]*bottom_y_offset, bottom_z))
    midpoint = (start + end) / 2
    
    # Direction vector and rotation
    direction = (end - start).normalized()
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('X', 'Z')
    
    # Create diagonal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=midpoint)
    diag = bpy.context.active_object
    diag.name = data["name"]
    diag.scale = (diagonal_l, diagonal_w, diagonal_d)
    diag.rotation_mode = 'QUATERNION'
    diag.rotation_quaternion = rot_quat
    
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'ACTIVE'
    diag.rigid_body.collision_shape = 'BOX'
    diagonals.append(diag)

# Create fixed constraints at joints
def create_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj_a.name}_{obj_b.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b

# Connect verticals to chords
for vert in verticals:
    create_fixed_constraint(vert, top)  # Top connection
    create_fixed_constraint(vert, bottom1)  # Bottom connections
    create_fixed_constraint(vert, bottom2)

# Connect diagonals to chords
for diag in diagonals:
    create_fixed_constraint(diag, top)
    create_fixed_constraint(diag, bottom1)
    create_fixed_constraint(diag, bottom2)

# Connect chords at ends (top to bottom via verticals already done)
create_fixed_constraint(top, verticals[0])  # Left end
create_fixed_constraint(top, verticals[2])  # Right end

# Apply distributed load to top chord (approximated as force at center)
top.rigid_body.use_gravity = True
# In headless mode, we apply initial velocity/force via animation or simulation settings
# We'll set up a force field for distributed load simulation
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, top_z + 0.5))
force_empty = bpy.context.active_object
force_empty.name = "Load_Force"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = -load_force  # Downward
force_empty.field.use_max_distance = True
force_empty.field.distance_max = 1.0
force_empty.field.falloff_power = 0.0

# Parent force field to top chord for distributed effect
force_empty.parent = top
force_empty.matrix_parent_inverse = top.matrix_world.inverted()

# Setup rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250  # Simulation duration

print("Fink truss construction complete. Structure ready for physics simulation.")