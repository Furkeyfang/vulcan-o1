import bpy
import math
import mathutils

# ========== PARAMETERS FROM SUMMARY ==========
span_total = 9.0
peak_height = 2.5
base_height = 0.0
top_chord_length = 4.5
top_chord_cross = 0.3
bottom_chord_length = 4.5
bottom_chord_cross = 0.3
diagonal_cross = 0.2
diagonal_length = 3.363
support_column_height = 2.5
support_column_cross = 0.3

top_chord_left_center = (-2.25, 0.0, 2.5)
top_chord_right_center = (2.25, 0.0, 2.5)
bottom_chord_left_center = (-2.25, 0.0, 0.0)
bottom_chord_right_center = (2.25, 0.0, 0.0)

diagonal1_midpoint = (-1.125, 0.0, 1.25)
diagonal2_midpoint = (-1.125, 0.0, 1.25)
diagonal3_midpoint = (1.125, 0.0, 1.25)
diagonal4_midpoint = (1.125, 0.0, 1.25)

support_left_center = (-4.5, 0.0, 1.25)
support_right_center = (4.5, 0.0, 1.25)

load_mass_total = 700.0
top_chord_mass_each = 350.0
simulation_frames = 100
max_deflection = 0.1

# ========== SCENE SETUP ==========
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# ========== HELPER FUNCTIONS ==========
def create_beam(name, location, length, cross_x, cross_z, rotation_angle=0.0, axis='X'):
    """Create a rectangular beam (cube) with given dimensions and rotation"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale to dimensions (default cube is 2x2x2, so divide by 2)
    beam.scale = (cross_x/2.0, length/2.0, cross_z/2.0)
    
    # Rotate if needed
    if rotation_angle != 0.0:
        if axis == 'X':
            beam.rotation_euler = (rotation_angle, 0, 0)
        elif axis == 'Y':
            beam.rotation_euler = (0, rotation_angle, 0)
        elif axis == 'Z':
            beam.rotation_euler = (0, 0, rotation_angle)
    
    return beam

def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    """Add rigid body physics to object"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

def create_fixed_constraint(obj1, obj2, location):
    """Create a fixed constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj1.name}_{obj2.name}"
    
    # Add rigid body constraint
    bpy.context.view_layer.objects.active = empty
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    return empty

# ========== CREATE GROUND ==========
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
add_rigidbody(ground, body_type='PASSIVE', mass=0.0)

# ========== CREATE SUPPORT COLUMNS ==========
support_left = create_beam(
    "Support_Left",
    support_left_center,
    support_column_height,
    support_column_cross,
    support_column_cross
)
add_rigidbody(support_left, body_type='PASSIVE', mass=0.0)

support_right = create_beam(
    "Support_Right",
    support_right_center,
    support_column_height,
    support_column_cross,
    support_column_cross
)
add_rigidbody(support_right, body_type='PASSIVE', mass=0.0)

# ========== CREATE TOP CHORD MEMBERS ==========
top_left = create_beam(
    "Top_Chord_Left",
    top_chord_left_center,
    top_chord_length,
    top_chord_cross,
    top_chord_cross
)
add_rigidbody(top_left, body_type='ACTIVE', mass=top_chord_mass_each)

top_right = create_beam(
    "Top_Chord_Right",
    top_chord_right_center,
    top_chord_length,
    top_chord_cross,
    top_chord_cross
)
add_rigidbody(top_right, body_type='ACTIVE', mass=top_chord_mass_each)

# ========== CREATE BOTTOM CHORD MEMBERS ==========
bottom_left = create_beam(
    "Bottom_Chord_Left",
    bottom_chord_left_center,
    bottom_chord_length,
    bottom_chord_cross,
    bottom_chord_cross
)
add_rigidbody(bottom_left, body_type='ACTIVE', mass=1.0)  # Light structural mass

bottom_right = create_beam(
    "Bottom_Chord_Right",
    bottom_chord_right_center,
    bottom_chord_length,
    bottom_chord_cross,
    bottom_chord_cross
)
add_rigidbody(bottom_right, body_type='ACTIVE', mass=1.0)

# ========== CREATE DIAGONAL WEB MEMBERS ==========
# Calculate rotation angles for diagonals (in radians)
diag_angle = math.atan2(peak_height, 2.25)  # 2.25 = horizontal distance

# Diagonal 1 (Top Left to Bottom Center)
diag1 = create_beam(
    "Diagonal_1",
    diagonal1_midpoint,
    diagonal_length,
    diagonal_cross,
    diagonal_cross,
    rotation_angle=-diag_angle,
    axis='Z'
)
add_rigidbody(diag1, body_type='ACTIVE', mass=0.5)

# Diagonal 2 (Top Center to Bottom Left)
diag2 = create_beam(
    "Diagonal_2",
    diagonal2_midpoint,
    diagonal_length,
    diagonal_cross,
    diagonal_cross,
    rotation_angle=diag_angle,
    axis='Z'
)
add_rigidbody(diag2, body_type='ACTIVE', mass=0.5)

# Diagonal 3 (Top Center to Bottom Right)
diag3 = create_beam(
    "Diagonal_3",
    diagonal3_midpoint,
    diagonal_length,
    diagonal_cross,
    diagonal_cross,
    rotation_angle=-diag_angle,
    axis='Z'
)
add_rigidbody(diag3, body_type='ACTIVE', mass=0.5)

# Diagonal 4 (Top Right to Bottom Center)
diag4 = create_beam(
    "Diagonal_4",
    diagonal4_midpoint,
    diagonal_length,
    diagonal_cross,
    diagonal_cross,
    rotation_angle=diag_angle,
    axis='Z'
)
add_rigidbody(diag4, body_type='ACTIVE', mass=0.5)

# ========== CREATE FIXED CONSTRAINTS AT JOINTS ==========
# Left End Joint (X=-4.5)
create_fixed_constraint(support_left, top_left, (-4.5, 0, 2.5))
create_fixed_constraint(support_left, bottom_left, (-4.5, 0, 0))

# Right End Joint (X=4.5)
create_fixed_constraint(support_right, top_right, (4.5, 0, 2.5))
create_fixed_constraint(support_right, bottom_right, (4.5, 0, 0))

# Center Top Joint (X=0, Z=2.5)
create_fixed_constraint(top_left, top_right, (0, 0, 2.5))
create_fixed_constraint(top_left, diag2, (0, 0, 2.5))
create_fixed_constraint(top_left, diag3, (0, 0, 2.5))

# Center Bottom Joint (X=0, Z=0)
create_fixed_constraint(bottom_left, bottom_right, (0, 0, 0))
create_fixed_constraint(bottom_left, diag1, (0, 0, 0))
create_fixed_constraint(bottom_left, diag4, (0, 0, 0))

# Left Mid Joint (X=-2.25, Z=2.5)
create_fixed_constraint(top_left, diag1, (-2.25, 0, 2.5))

# Left Mid Bottom Joint (X=-2.25, Z=0)
create_fixed_constraint(bottom_left, diag2, (-2.25, 0, 0))

# Right Mid Joint (X=2.25, Z=2.5)
create_fixed_constraint(top_right, diag4, (2.25, 0, 2.5))

# Right Mid Bottom Joint (X=2.25, Z=0)
create_fixed_constraint(bottom_right, diag3, (2.25, 0, 0))

# ========== SIMULATION SETUP ==========
# Set physics parameters for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = simulation_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print("Scissor truss roof construction complete. Simulation baked for", simulation_frames, "frames.")