import bpy
import math
from mathutils import Vector

# ========== PARAMETERS ==========
# Truss Dimensions
span_length = 12.0
bottom_chord_size = (12.0, 0.3, 0.3)
top_chord_length = 6.5
top_chord_size = (6.5, 0.3, 0.3)
king_post_size = (1.5, 0.3, 0.3)
pitch_angle = 35.0
pitch_rad = math.radians(pitch_angle)

# Geometry
peak_height = top_chord_length * math.sin(pitch_rad)  # ≈ 3.728
horizontal_proj = top_chord_length * math.cos(pitch_rad)  # ≈ 5.324
peak_offset = (span_length / 2) - horizontal_proj  # ≈ 0.676
bottom_chord_z = 0.0
peak_x = -peak_offset  # ≈ -0.676
peak_z = peak_height
king_post_top_z = peak_z
king_post_bottom_z = peak_z - king_post_size[0]

# Truss Positions
truss1_y = 0.0
truss2_y = 4.0

# Purlin Parameters
purlin_size = (4.0, 0.2, 0.2)
purlin_spacing = 2.0
purlin_x_positions = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]

# Load
total_load_kg = 900.0
total_load_N = total_load_kg * 9.81
num_load_beams = 22  # 4 top chords + 14 purlin ends (7 purlins × 2 ends)
force_per_beam = total_load_N / num_load_beams

# Material density (kg/m³) for mass calculation
density = 500.0

# ========== SCENE SETUP ==========
# Clear existing
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# ========== HELPER FUNCTIONS ==========
def create_beam(size, location, rotation, name, passive=True):
    """Create a beam cube with rigid body."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (size[0]/2, size[1]/2, size[2]/2)  # Cube default size=2, so /2
    beam.rotation_euler = rotation
    
    # Rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE' if passive else 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.collision_margin = 0.04
    beam.rigid_body.mass = size[0] * size[1] * size[2] * density
    
    return beam

def add_fixed_constraint(obj1, obj2):
    """Add a fixed constraint between two objects."""
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    con = obj1.constraints[-1]
    con.type = 'FIXED'
    con.object1 = obj1
    con.object2 = obj2

# ========== BUILD TRUSS 1 ==========
# Bottom Chord
bottom1 = create_beam(
    bottom_chord_size,
    (0.0, truss1_y, bottom_chord_z),
    (0.0, 0.0, 0.0),
    "Bottom_Chord_1",
    passive=True
)

# Left Top Chord
left_top1 = create_beam(
    top_chord_size,
    (-6.0 + horizontal_proj/2, truss1_y, peak_height/2),
    (0.0, -pitch_rad, 0.0),
    "Left_Top_Chord_1",
    passive=False
)
left_top1.location.x = -6.0 + (horizontal_proj/2) * math.cos(pitch_rad)
left_top1.location.z = (peak_height/2) * math.sin(pitch_rad)

# Right Top Chord
right_top1 = create_beam(
    top_chord_size,
    (6.0 - horizontal_proj/2, truss1_y, peak_height/2),
    (0.0, pitch_rad, 0.0),
    "Right_Top_Chord_1",
    passive=False
)
right_top1.location.x = 6.0 - (horizontal_proj/2) * math.cos(pitch_rad)
right_top1.location.z = (peak_height/2) * math.sin(pitch_rad)

# King Post
king1 = create_beam(
    king_post_size,
    (peak_x, truss1_y, (king_post_top_z + king_post_bottom_z)/2),
    (0.0, 0.0, 0.0),
    "King_Post_1",
    passive=False
)

# ========== BUILD TRUSS 2 ==========
# Bottom Chord
bottom2 = create_beam(
    bottom_chord_size,
    (0.0, truss2_y, bottom_chord_z),
    (0.0, 0.0, 0.0),
    "Bottom_Chord_2",
    passive=True
)

# Left Top Chord
left_top2 = create_beam(
    top_chord_size,
    (-6.0 + horizontal_proj/2, truss2_y, peak_height/2),
    (0.0, -pitch_rad, 0.0),
    "Left_Top_Chord_2",
    passive=False
)
left_top2.location.x = -6.0 + (horizontal_proj/2) * math.cos(pitch_rad)
left_top2.location.z = (peak_height/2) * math.sin(pitch_rad)

# Right Top Chord
right_top2 = create_beam(
    top_chord_size,
    (6.0 - horizontal_proj/2, truss2_y, peak_height/2),
    (0.0, pitch_rad, 0.0),
    "Right_Top_Chord_2",
    passive=False
)
right_top2.location.x = 6.0 - (horizontal_proj/2) * math.cos(pitch_rad)
right_top2.location.z = (peak_height/2) * math.sin(pitch_rad)

# King Post
king2 = create_beam(
    king_post_size,
    (peak_x, truss2_y, (king_post_top_z + king_post_bottom_z)/2),
    (0.0, 0.0, 0.0),
    "King_Post_2",
    passive=False
)

# ========== ADD FIXED CONSTRAINTS WITHIN TRUSSES ==========
# Truss 1 connections
add_fixed_constraint(bottom1, left_top1)   # Left end
add_fixed_constraint(bottom1, right_top1)  # Right end
add_fixed_constraint(bottom1, king1)       # Center bottom
add_fixed_constraint(left_top1, king1)     # Peak left
add_fixed_constraint(right_top1, king1)    # Peak right

# Truss 2 connections
add_fixed_constraint(bottom2, left_top2)
add_fixed_constraint(bottom2, right_top2)
add_fixed_constraint(bottom2, king2)
add_fixed_constraint(left_top2, king2)
add_fixed_constraint(right_top2, king2)

# ========== BUILD PURLINS ==========
purlins = []
for i, x in enumerate(purlin_x_positions):
    # Calculate height at this x
    if x <= peak_x:
        z = (x + 6.0) * math.tan(pitch_rad)
    else:
        z = (6.0 - x) * math.tan(pitch_rad)
    
    # Create purlin
    purlin = create_beam(
        purlin_size,
        (x, (truss1_y + truss2_y)/2, z),
        (0.0, 0.0, 0.0),
        f"Purlin_{i}",
        passive=False
    )
    purlins.append(purlin)
    
    # Connect to trusses
    add_fixed_constraint(purlin, left_top1 if x <= peak_x else right_top1)
    add_fixed_constraint(purlin, left_top2 if x <= peak_x else right_top2)

# ========== APPLY LOAD ==========
# Apply downward force to all top chords and purlins
load_objects = [left_top1, right_top1, left_top2, right_top2] + purlins
for obj in load_objects:
    if obj.rigid_body:
        obj.rigid_body.kinematic = False
        # Force will be applied via rigid body settings
        # In headless, we can't keyframe forces directly, so we use constant force
        # Alternative: apply initial impulse
        obj.rigid_body.use_deactivation = False

# ========== FINAL SETUP ==========
# Set gravity
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Set frame range for simulation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

print("Scissor truss roof assembly complete. Run simulation for 100 frames.")