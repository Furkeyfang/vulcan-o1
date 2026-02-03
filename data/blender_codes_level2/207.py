import bpy
import math
from mathutils import Vector, Matrix

# ========== PARAMETERS ==========
span_length = 16.0
panel_count = 8
panel_width = span_length / panel_count
ground_z = 0.0
support_height = 3.0
support_cross = 0.5
truss_height = 2.0
bottom_chord_z = 3.0
top_chord_z = bottom_chord_z + truss_height
chord_dim = (2.0, 0.3, 0.3)        # X=length, Y=width, Z=height
vert_dim = (0.2, 0.2, 2.0)         # X=width, Y=depth, Z=height
diag_dim = (0.2, 0.2, 2.0)         # Will be rotated and scaled
total_load_kg = 1500.0
gravity = 9.81
load_per_chunk = total_load_kg / panel_count
force_per_chunk = load_per_chunk * gravity
sim_frames = 100
max_deflection = 0.01

# ========== SCENE SETUP ==========
# Clear existing
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -gravity)

# ========== HELPER FUNCTIONS ==========
def create_cube(name, location, scale, rotation=(0,0,0)):
    """Create a cube with given transform"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    return obj

def add_rigidbody(obj, type='ACTIVE', mass=10.0, collision_shape='BOX'):
    """Add rigid body physics"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = type
    obj.rigid_body.collision_shape = collision_shape
    obj.rigid_body.mass = mass
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1
    return obj

def add_fixed_constraint(obj_a, obj_b):
    """Create fixed constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Constrain empty to obj_a
    constraint = empty.constraints.new(type='RIGID_BODY_JOINT')
    constraint.object1 = empty
    constraint.object2 = obj_a
    constraint.type = 'FIXED'
    
    # Constrain obj_b to empty
    constraint = obj_b.constraints.new(type='RIGID_BODY_JOINT')
    constraint.object1 = obj_b
    constraint.object2 = empty
    constraint.type = 'FIXED'
    return empty

# ========== CREATE SUPPORT COLUMNS ==========
support_left = create_cube(
    "Support_Left",
    location=(0.0, 0.0, support_height/2),
    scale=(support_cross, support_cross, support_height)
)
add_rigidbody(support_left, type='PASSIVE', mass=1000.0)

support_right = create_cube(
    "Support_Right",
    location=(span_length, 0.0, support_height/2),
    scale=(support_cross, support_cross, support_height)
)
add_rigidbody(support_right, type='PASSIVE', mass=1000.0)

# ========== CREATE BOTTOM CHORD ==========
bottom_chords = []
for i in range(panel_count):
    x_pos = (i * panel_width) + (panel_width / 2)
    chord = create_cube(
        f"Bottom_Chord_{i}",
        location=(x_pos, 0.0, bottom_chord_z),
        scale=chord_dim
    )
    add_rigidbody(chord, mass=chord_dim[0]*chord_dim[1]*chord_dim[2]*2500)
    bottom_chords.append(chord)

# ========== CREATE TOP CHORD ==========
top_chords = []
for i in range(panel_count):
    x_pos = (i * panel_width) + (panel_width / 2)
    chord = create_cube(
        f"Top_Chord_{i}",
        location=(x_pos, 0.0, top_chord_z),
        scale=chord_dim
    )
    add_rigidbody(chord, mass=chord_dim[0]*chord_dim[1]*chord_dim[2]*2500)
    top_chords.append(chord)

# ========== CREATE VERTICAL MEMBERS ==========
verticals = []
for i in range(panel_count + 1):  # 9 verticals for 8 panels
    x_pos = i * panel_width
    vert = create_cube(
        f"Vertical_{i}",
        location=(x_pos, 0.0, (bottom_chord_z + top_chord_z)/2),
        scale=vert_dim
    )
    add_rigidbody(vert, mass=vert_dim[0]*vert_dim[1]*vert_dim[2]*2500)
    verticals.append(vert)

# ========== CREATE DIAGONAL MEMBERS ==========
diagonals = []
diag_length = math.sqrt(panel_width**2 + truss_height**2)
scale_factor = diag_length / 2.0  # Original cube is 2m default

for i in range(panel_count):
    if i < panel_count / 2:  # Left half: slope down-right
        top_x = i * panel_width
        bottom_x = (i + 1) * panel_width
        angle = math.atan2(-truss_height, panel_width)  # Negative for downward
    else:  # Right half: slope down-left
        top_x = (i + 1) * panel_width
        bottom_x = i * panel_width
        angle = math.atan2(-truss_height, -panel_width)
    
    # Calculate center position
    center_x = (top_x + bottom_x) / 2
    center_z = (top_chord_z + bottom_chord_z) / 2
    
    diag = create_cube(
        f"Diagonal_{i}",
        location=(center_x, 0.0, center_z),
        scale=(diag_dim[0], diag_dim[1], scale_factor),
        rotation=(0, angle, 0)
    )
    add_rigidbody(diag, mass=diag_dim[0]*diag_dim[1]*diag_length*2500)
    diagonals.append(diag)

# ========== CREATE JOINTS WITH FIXED CONSTRAINTS ==========
# Connect bottom chords to supports
add_fixed_constraint(support_left, bottom_chords[0])
add_fixed_constraint(support_right, bottom_chords[-1])

# Connect adjacent bottom chords
for i in range(len(bottom_chords)-1):
    add_fixed_constraint(bottom_chords[i], bottom_chords[i+1])

# Connect adjacent top chords
for i in range(len(top_chords)-1):
    add_fixed_constraint(top_chords[i], top_chords[i+1])

# Connect verticals to chords at joints
for i, vert in enumerate(verticals):
    x_pos = i * panel_width
    
    # Connect to bottom chord (find nearest chord)
    if i == 0:
        bottom_target = bottom_chords[0]
    elif i == len(verticals)-1:
        bottom_target = bottom_chords[-1]
    else:
        # Vertical is between two chords, connect to both
        left_chord = bottom_chords[i-1]
        right_chord = bottom_chords[i]
        add_fixed_constraint(vert, left_chord)
        add_fixed_constraint(vert, right_chord)
        bottom_target = None
    
    if bottom_target:
        add_fixed_constraint(vert, bottom_target)
    
    # Connect to top chord
    if i == 0:
        top_target = top_chords[0]
    elif i == len(verticals)-1:
        top_target = top_chords[-1]
    else:
        left_chord = top_chords[i-1]
        right_chord = top_chords[i]
        add_fixed_constraint(vert, left_chord)
        add_fixed_constraint(vert, right_chord)
        top_target = None
    
    if top_target:
        add_fixed_constraint(vert, top_target)

# Connect diagonals to chords
for i, diag in enumerate(diagonals):
    if i < panel_count / 2:  # Left half
        top_idx = i
        bottom_idx = i + 1
    else:  # Right half
        top_idx = i + 1
        bottom_idx = i
    
    # Connect to top chord
    if top_idx < len(top_chords):
        add_fixed_constraint(diag, top_chords[top_idx])
    
    # Connect to bottom chord
    if bottom_idx < len(bottom_chords):
        add_fixed_constraint(diag, bottom_chords[bottom_idx])

# ========== APPLY LOAD ==========
for i, chord in enumerate(top_chords):
    chord.rigid_body.use_gravity = True
    # Apply additional downward force equivalent to distributed load
    bpy.context.view_layer.objects.active = chord
    bpy.ops.object.forcefield_add(type='FORCE')
    chord.field.strength = -force_per_chunk
    chord.field.use_max_distance = True
    chord.field.distance_max = 0.5  # Only affect nearby objects
    chord.field.falloff_power = 0.0

# ========== SIMULATION SETUP ==========
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.point_cache.frame_end = sim_frames
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Pratt truss construction complete.")
print(f"Applied load: {total_load_kg}kg ({total_load_kg * gravity:.1f}N) distributed")
print(f"Simulation will run for {sim_frames} frames")
print(f"Target max deflection: {max_deflection}m")