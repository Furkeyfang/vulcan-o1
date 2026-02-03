import bpy
import math
from mathutils import Vector, Euler

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Enable rigid body physics
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

# ========== PARAMETERS (from summary) ==========
frame_length = 6.0
frame_width = 2.0
frame_height = 1.0
member_cross = 0.1
chord_length_x = 6.0
chord_length_y = 2.0
top_z = 1.0
bottom_z = 0.0
post_positions = [
    (-3.0, -1.0), (-3.0, 0.0), (-3.0, 1.0),
    (0.0, -1.0), (0.0, 1.0),
    (3.0, -1.0), (3.0, 0.0), (3.0, 1.0)
]
post_height = 1.0
brace_length = 1.414
brace_angle = 45.0
load_mass = 300.0
plate_size = (1.0, 1.0, 0.05)
plate_center = (0.0, 0.0, 1.025)
sim_frames = 100

# ========== HELPER FUNCTIONS ==========
def create_rigid_body(obj, body_type='PASSIVE', mass=1.0):
    """Add rigid body physics to object"""
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    if body_type == 'ACTIVE':
        obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'
    return obj

def create_fixed_constraint(obj1, obj2):
    """Create FIXED constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{obj1.name}_{obj2.name}"
    
    # Add constraint component
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    
    return constraint

# ========== CREATE HORIZONTAL CHORDS ==========
chords = []
# Top chords (along X at Y=-1 and Y=1)
for y in [-1.0, 1.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, top_z))
    chord = bpy.context.active_object
    chord.scale = (chord_length_x, member_cross, member_cross)
    chord.name = f"TopChord_X_y{y}"
    create_rigid_body(chord)
    chords.append(chord)

# Top chords (along Y at X=-3 and X=3)
for x in [-3.0, 3.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, top_z))
    chord = bpy.context.active_object
    chord.scale = (member_cross, chord_length_y, member_cross)
    chord.name = f"TopChord_Y_x{x}"
    create_rigid_body(chord)
    chords.append(chord)

# Bottom chords (same pattern at Z=0)
for y in [-1.0, 1.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, bottom_z))
    chord = bpy.context.active_object
    chord.scale = (chord_length_x, member_cross, member_cross)
    chord.name = f"BotChord_X_y{y}"
    create_rigid_body(chord)
    chords.append(chord)

for x in [-3.0, 3.0]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, bottom_z))
    chord = bpy.context.active_object
    chord.scale = (member_cross, chord_length_y, member_cross)
    chord.name = f"BotChord_Y_x{x}"
    create_rigid_body(chord)
    chords.append(chord)

# ========== CREATE VERTICAL POSTS ==========
posts = []
for i, (x, y) in enumerate(post_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, post_height/2))
    post = bpy.context.active_object
    post.scale = (member_cross, member_cross, post_height)
    post.name = f"Post_{i}"
    create_rigid_body(post)
    posts.append(post)

# ========== CREATE DIAGONAL BRACES ==========
braces = []
# Braces on long sides (Y = -1 and Y = 1)
for y in [-1.0, 1.0]:
    for x_offset in [-1.5, 1.5]:  # Midpoints of each half-span
        # Create at bottom then rotate
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_offset, y, 0.5))
        brace = bpy.context.active_object
        brace.scale = (brace_length, member_cross, member_cross)
        
        # Rotate 45° about Y-axis
        angle_rad = math.radians(brace_angle) if x_offset > 0 else -math.radians(brace_angle)
        brace.rotation_euler = Euler((0, angle_rad, 0), 'XYZ')
        
        brace.name = f"Brace_Long_y{y}_x{x_offset}"
        create_rigid_body(brace)
        braces.append(brace)

# Braces on short sides (X = -3 and X = 3)
for x in [-3.0, 3.0]:
    for y_offset in [-0.5, 0.5]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y_offset, 0.5))
        brace = bpy.context.active_object
        brace.scale = (member_cross, brace_length, member_cross)
        
        # Rotate 45° about X-axis
        angle_rad = math.radians(brace_angle) if y_offset > 0 else -math.radians(brace_angle)
        brace.rotation_euler = Euler((angle_rad, 0, 0), 'XYZ')
        
        brace.name = f"Brace_Short_x{x}_y{y_offset}"
        create_rigid_body(brace)
        braces.append(brace)

# ========== CREATE LOAD PLATE ==========
bpy.ops.mesh.primitive_cube_add(size=1, location=plate_center)
load_plate = bpy.context.active_object
load_plate.scale = plate_size
load_plate.name = "Load_Plate"
create_rigid_body(load_plate, 'ACTIVE', load_mass)

# ========== CREATE FIXED CONSTRAINTS AT JOINTS ==========
# Group objects by approximate location (snap to grid)
from collections import defaultdict
joint_dict = defaultdict(list)

all_members = chords + posts + braces
for obj in all_members:
    # Snap location to nearest 0.1m grid for joint matching
    loc = obj.location
    snap_loc = (round(loc.x, 1), round(loc.y, 1), round(loc.z, 1))
    joint_dict[snap_loc].append(obj)

# Create constraints for joints with >1 member
for joint_loc, objects in joint_dict.items():
    if len(objects) >= 2:
        base_obj = objects[0]
        for other_obj in objects[1:]:
            # Skip if constraint already exists (simple check)
            constraint_name = f"Fix_{base_obj.name}_{other_obj.name}"
            if constraint_name not in bpy.data.objects:
                create_fixed_constraint(base_obj, other_obj)

# ========== SIMULATION SETUP ==========
# Set simulation end frame
bpy.context.scene.frame_end = sim_frames

# Optional: Bake simulation for verification
print("Box truss construction complete. Run simulation with:")
print(f"blender --background --python-expr 'import bpy; bpy.ops.ptcache.bake_all()'")