import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
column_dim = (0.5, 0.5, 22.0)
column_positions = [(-1.0, -1.0, 11.0), (-1.0, 1.0, 11.0), (1.0, 1.0, 11.0), (1.0, -1.0, 11.0)]

beam_horiz_dim = (2.0, 0.5, 0.5)
beam_bottom_z = 0.0
beam_top_z = 22.0
beam_horiz_centers = [(-1.0, 0.0, beam_bottom_z), (0.0, 1.0, beam_bottom_z),
                      (1.0, 0.0, beam_bottom_z), (0.0, -1.0, beam_bottom_z)]

diagonal_length = 2.828
diagonal_dim = (diagonal_length, 0.5, 0.5)
diagonal_centers_bottom = [(0.0, 0.0, beam_bottom_z), (0.0, 0.0, beam_bottom_z)]
diagonal_rotations_bottom = [(0.0, 0.0, math.pi/4), (0.0, 0.0, -math.pi/4)]
diagonal_centers_top = [(0.0, 0.0, beam_top_z), (0.0, 0.0, beam_top_z)]
diagonal_rotations_top = [(0.0, 0.0, math.pi/4), (0.0, 0.0, -math.pi/4)]

platform_dim = (2.0, 2.0, 0.5)
platform_center = (0.0, 0.0, 22.25)
load_mass = 5000.0
simulation_frames = 500

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Helper function to create beam with physics and return object
def create_beam(name, location, scale, rotation=(0,0,0), rigid_body_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    return obj

# Create columns
columns = []
for i, pos in enumerate(column_positions):
    col = create_beam(f"Column_{i+1}", pos, column_dim)
    columns.append(col)

# Create bottom horizontal beams
bottom_beams = []
for i, center in enumerate(beam_horiz_centers):
    # Determine orientation: beams along Y for X=-1 and X=1, beams along X for Y=-1 and Y=1
    beam = create_beam(f"BottomBeam_{i+1}", center, beam_horiz_dim)
    bottom_beams.append(beam)

# Create top horizontal beams
top_beams = []
for i, center in enumerate(beam_horiz_centers):
    top_center = (center[0], center[1], beam_top_z)
    beam = create_beam(f"TopBeam_{i+1}", top_center, beam_horiz_dim)
    top_beams.append(beam)

# Create bottom diagonal braces
bottom_diagonals = []
for i in range(2):
    diag = create_beam(f"BottomDiagonal_{i+1}", 
                      diagonal_centers_bottom[i], 
                      diagonal_dim,
                      diagonal_rotations_bottom[i])
    bottom_diagonals.append(diag)

# Create top diagonal braces
top_diagonals = []
for i in range(2):
    diag = create_beam(f"TopDiagonal_{i+1}", 
                      diagonal_centers_top[i], 
                      diagonal_dim,
                      diagonal_rotations_top[i])
    top_diagonals.append(diag)

# Create load platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_center)
platform = bpy.context.active_object
platform.name = "LoadPlatform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass

# Create fixed constraints between connected elements
def add_fixed_constraint(obj_a, obj_b):
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Connect columns to ground (implicit via PASSIVE rigid body at Z=0)
# No explicit constraint needed since columns are passive and base at Z=0

# Connect columns to bottom beams (each beam connects two adjacent columns)
# BottomBeam1 connects Column1 and Column2 at (-1,0,0)
add_fixed_constraint(columns[0], bottom_beams[0])
add_fixed_constraint(columns[1], bottom_beams[0])
# BottomBeam2 connects Column2 and Column3 at (0,1,0)
add_fixed_constraint(columns[1], bottom_beams[1])
add_fixed_constraint(columns[2], bottom_beams[1])
# BottomBeam3 connects Column3 and Column4 at (1,0,0)
add_fixed_constraint(columns[2], bottom_beams[2])
add_fixed_constraint(columns[3], bottom_beams[2])
# BottomBeam4 connects Column4 and Column1 at (0,-1,0)
add_fixed_constraint(columns[3], bottom_beams[3])
add_fixed_constraint(columns[0], bottom_beams[3])

# Connect columns to top beams
add_fixed_constraint(columns[0], top_beams[0])
add_fixed_constraint(columns[1], top_beams[0])
add_fixed_constraint(columns[1], top_beams[1])
add_fixed_constraint(columns[2], top_beams[1])
add_fixed_constraint(columns[2], top_beams[2])
add_fixed_constraint(columns[3], top_beams[2])
add_fixed_constraint(columns[3], top_beams[3])
add_fixed_constraint(columns[0], top_beams[3])

# Connect diagonal braces to columns
# Bottom diagonal1 connects Column1 (-1,-1,0) and Column3 (1,1,0)
add_fixed_constraint(columns[0], bottom_diagonals[0])
add_fixed_constraint(columns[2], bottom_diagonals[0])
# Bottom diagonal2 connects Column2 (-1,1,0) and Column4 (1,-1,0)
add_fixed_constraint(columns[1], bottom_diagonals[1])
add_fixed_constraint(columns[3], bottom_diagonals[1])
# Top diagonal1 connects Column1 (-1,-1,22) and Column3 (1,1,22)
add_fixed_constraint(columns[0], top_diagonals[0])
add_fixed_constraint(columns[2], top_diagonals[0])
# Top diagonal2 connects Column2 (-1,1,22) and Column4 (1,-1,22)
add_fixed_constraint(columns[1], top_diagonals[1])
add_fixed_constraint(columns[3], top_diagonals[1])

# Connect platform to top structure (constrain to all four top beams for stability)
for top_beam in top_beams:
    add_fixed_constraint(platform, top_beam)

# Set gravity and simulation parameters
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.gravity[2] = -9.81  # Earth gravity in Z
bpy.context.scene.frame_end = simulation_frames

# Bake simulation for headless verification (optional)
# bpy.ops.ptcache.bake_all(bake=True)

print(f"Steel frame structure created with {len(columns)} columns, {len(bottom_beams)+len(top_beams)} horizontal beams, {len(bottom_diagonals)+len(top_diagonals)} diagonal braces, and 1 load platform.")
print(f"Structure ready for {simulation_frames}-frame simulation with {load_mass} kg load.")