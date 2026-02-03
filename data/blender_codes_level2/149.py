import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract variables from parameter summary
W = frame_width
D = frame_depth
H = frame_height

col_x = col_size_x
col_y = col_size_y
col_z = col_size_z

beam_x = beam_size_x
beam_y = beam_size_y
beam_z = beam_size_z

brace_dia = brace_diameter

str_offset = stringer_offset
str_w = stringer_width
str_d = stringer_depth
str_len = stringer_length

step_w = step_width
step_d = step_depth
step_t = step_thickness
step_spc = step_spacing
n_steps = num_steps

steel_rho = steel_density
live_mass = live_load_mass

# Helper function to create steel beams with physics
def create_beam(name, size, location, rotation=(0,0,0), rigidbody_type='ACTIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = Vector(size) / 2  # Cube default size=2, so scale by half dimensions
    
    # Apply rotation
    beam.rotation_euler = rotation
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = rigidbody_type
    beam.rigid_body.mass = size[0] * size[1] * size[2] * steel_rho
    beam.rigid_body.collision_shape = 'BOX'
    
    return beam

# Create foundation plane (passive)
bpy.ops.mesh.primitive_plane_add(size=10, location=(0,0,-0.1))
foundation = bpy.context.active_object
foundation.name = "Foundation"
bpy.ops.rigidbody.object_add()
foundation.rigid_body.type = 'PASSIVE'

# Create 4 vertical columns
columns = []
col_positions = [
    (-W/2, -D/2, H/2),
    (W/2, -D/2, H/2),
    (-W/2, D/2, H/2),
    (W/2, D/2, H/2)
]

for i, pos in enumerate(col_positions):
    col = create_beam(f"Column_{i+1}", (col_x, col_y, col_z), pos, rigidbody_type='PASSIVE')
    columns.append(col)

# Create bottom perimeter beams (at Z = col_z/2 = 0.1m)
bottom_beams = []
beam_z_pos = col_z/2  # 0.1m
beam_positions = [
    (0, -D/2, beam_z_pos),  # Front beam (Y negative)
    (0, D/2, beam_z_pos),   # Back beam (Y positive)
    (-W/2, 0, beam_z_pos),  # Left beam (X negative)
    (W/2, 0, beam_z_pos)    # Right beam (X positive)
]

beam_sizes = [
    (W, beam_y, beam_z),  # X-direction beams
    (W, beam_y, beam_z),
    (beam_x, D, beam_z),  # Y-direction beams (using beam_x for consistency)
    (beam_x, D, beam_z)
]

rotations = [
    (0,0,0),
    (0,0,0),
    (0,0,0),
    (0,0,0)
]

for i, (pos, size, rot) in enumerate(zip(beam_positions, beam_sizes, rotations)):
    beam = create_beam(f"BottomBeam_{i+1}", size, pos, rot, 'PASSIVE')
    bottom_beams.append(beam)

# Create top perimeter beams (at Z = H - col_z/2 = 13.9m)
top_z_pos = H - col_z/2
top_beam_positions = [
    (0, -D/2, top_z_pos),
    (0, D/2, top_z_pos),
    (-W/2, 0, top_z_pos),
    (W/2, 0, top_z_pos)
]

for i, (pos, size, rot) in enumerate(zip(top_beam_positions, beam_sizes, rotations)):
    beam = create_beam(f"TopBeam_{i+1}", size, pos, rot, 'PASSIVE')

# Create diagonal braces (45° in XZ planes at Y = ±D/2)
# Brace length = √(W² + W²) = W√2 = 4.243m (since ΔZ = ΔX for 45°)
brace_length = W * math.sqrt(2)
brace_height = W  # Vertical rise equals horizontal span

for y_pos in [-D/2, D/2]:
    # Calculate rotation angle: atan2(ΔZ, ΔX) = atan2(W, W) = 45°
    angle = math.atan2(brace_height, W)
    
    # Start at left column, end at right column
    start_x = -W/2
    end_x = W/2
    start_z = beam_z_pos + brace_dia/2  # Just above bottom beam
    end_z = start_z + brace_height
    
    # Midpoint for placement
    mid_x = (start_x + end_x) / 2
    mid_z = (start_z + end_z) / 2
    
    # Create cylindrical brace
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=brace_dia/2,
        depth=brace_length,
        location=(mid_x, y_pos, mid_z)
    )
    brace = bpy.context.active_object
    brace.name = f"Brace_Y{y_pos}"
    
    # Rotate to 45° in XZ plane
    brace.rotation_euler = (0, angle, 0)
    
    # Add physics
    bpy.ops.rigidbody.object_add()
    brace.rigid_body.type = 'PASSIVE'
    volume = math.pi * (brace_dia/2)**2 * brace_length
    brace.rigid_body.mass = volume * steel_rho

# Create stair stringers
stringers = []
str_start = Vector((-W/2 + str_offset, -D/2, 0))
str_end = Vector((-W/2 + str_offset, D/2, H))
str_dir = (str_end - str_start).normalized()

# Calculate angle for rotation
str_angle = math.atan2(H, D)  # In YZ plane

for x_offset in [str_offset, W - str_offset]:
    # Position at left and right sides
    start = Vector((-W/2 + x_offset, -D/2, 0))
    end = Vector((-W/2 + x_offset, D/2, H))
    mid = (start + end) / 2
    
    # Create stringer
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    stringer = bpy.context.active_object
    stringer.name = f"Stringer_X{x_offset}"
    
    # Scale to dimensions
    stringer.scale = (str_w/2, str_len/2, str_d/2)
    
    # Rotate to follow stair angle (around X-axis)
    stringer.rotation_euler = (str_angle, 0, 0)
    
    # Add physics
    bpy.ops.rigidbody.object_add()
    stringer.rigid_body.type = 'PASSIVE'
    vol = str_w * str_len * str_d
    stringer.rigid_body.mass = vol * steel_rho
    stringers.append(stringer)

# Create step supports
step_mass = (step_w * step_d * step_t * steel_rho) + (live_mass / n_steps)

for i in range(n_steps):
    z_pos = (i + 1) * step_spc
    
    # Interpolate along stringer path
    t = z_pos / H
    y_pos = -D/2 + t * D
    
    # Create step at both stringer positions
    for x_offset in [str_offset, W - str_offset]:
        x_pos = -W/2 + x_offset
        
        step = create_beam(
            f"Step_{i+1}_X{x_offset}",
            (step_w, step_d, step_t),
            (x_pos, y_pos, z_pos),
            rigidbody_type='ACTIVE'
        )
        step.rigid_body.mass = step_mass

# Set gravity for simulation
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)

# Set collision margins
for obj in bpy.context.scene.objects:
    if hasattr(obj, 'rigid_body') and obj.rigid_body:
        obj.rigid_body.collision_margin = 0.001

print("Steel stairwell frame construction complete. Ready for physics simulation.")