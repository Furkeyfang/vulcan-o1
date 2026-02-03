import bpy
import math
from mathutils import Matrix

# 1. Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define variables from parameter summary
span_length = 6.0
slope_height = 1.5
platform_dim = (6.0, 1.0, 0.05)
platform_center_z = 0.725
platform_rotation_y = 0.245  # 14.04° in radians
truss_offset_y = 0.5
chord_dim = (6.0, 0.2, 0.2)
vert_strut_dim = (0.2, 0.2, 0.8)
diag_brace_length = 1.2806
diag_brace_dim = (diag_brace_length, 0.2, 0.2)
num_segments = 6
segment_length = 1.0
load_mass_kg = 450
load_position_x = 3.0
load_position_y = 0.0
load_position_z = 0.75  # Platform top at X=3
simulation_frames = 100

# 3. Create Platform (sloped walking surface)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(span_length/2, 0, platform_center_z))
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
platform.rotation_euler = (0, platform_rotation_y, 0)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'

# 4. Function to create one truss side at given Y offset
def create_truss_side(y_offset, suffix):
    # Calculate joint positions
    joint_positions_top = []
    joint_positions_bottom = []
    for i in range(num_segments + 1):
        x_pos = i * segment_length
        # Z positions follow slope: top chord center at -0.15 + 0.25*x
        z_top = -0.15 + (slope_height/span_length) * x_pos
        z_bottom = z_top - 0.8  # bottom chord center 0.8m below top
        joint_positions_top.append((x_pos, y_offset, z_top))
        joint_positions_bottom.append((x_pos, y_offset, z_bottom))
    
    # Create Top Chord
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(span_length/2, y_offset, 0))
    top_chord = bpy.context.active_object
    top_chord.name = f"TopChord_{suffix}"
    top_chord.scale = chord_dim
    # Rotate to match slope
    top_chord.rotation_euler = (0, platform_rotation_y, 0)
    # Adjust position so it passes through top joints
    # The chord's center after rotation should be at average of top joints
    avg_z_top = (joint_positions_top[0][2] + joint_positions_top[-1][2]) / 2
    top_chord.location = (span_length/2, y_offset, avg_z_top)
    bpy.ops.rigidbody.object_add()
    top_chord.rigid_body.type = 'PASSIVE'
    
    # Create Bottom Chord
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(span_length/2, y_offset, 0))
    bottom_chord = bpy.context.active_object
    bottom_chord.name = f"BottomChord_{suffix}"
    bottom_chord.scale = chord_dim
    bottom_chord.rotation_euler = (0, platform_rotation_y, 0)
    avg_z_bottom = (joint_positions_bottom[0][2] + joint_positions_bottom[-1][2]) / 2
    bottom_chord.location = (span_length/2, y_offset, avg_z_bottom)
    bpy.ops.rigidbody.object_add()
    bottom_chord.rigid_body.type = 'PASSIVE'
    
    # Create Vertical Struts
    verticals = []
    for i, (x_pos, y_pos, z_top) in enumerate(joint_positions_top):
        z_bottom = joint_positions_bottom[i][2]
        # Vertical strut center is midpoint between top and bottom joints
        z_center = (z_top + z_bottom) / 2
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, y_offset, z_center))
        vert = bpy.context.active_object
        vert.name = f"Vertical_{i}_{suffix}"
        vert.scale = vert_strut_dim
        bpy.ops.rigidbody.object_add()
        vert.rigid_body.type = 'PASSIVE'
        verticals.append(vert)
    
    # Create Diagonal Braces (alternating direction)
    diagonals = []
    for i in range(num_segments):
        if i % 2 == 0:  # Downward slope: connect top joint i to bottom joint i+1
            start_pos = joint_positions_top[i]
            end_pos = joint_positions_bottom[i+1]
        else:  # Upward slope: connect bottom joint i to top joint i+1
            start_pos = joint_positions_bottom[i]
            end_pos = joint_positions_top[i+1]
        
        # Calculate center and rotation
        center = ((start_pos[0] + end_pos[0])/2,
                  (start_pos[1] + end_pos[1])/2,
                  (start_pos[2] + end_pos[2])/2)
        
        # Vector from start to end
        dx = end_pos[0] - start_pos[0]
        dz = end_pos[2] - start_pos[2]
        length = math.sqrt(dx**2 + dz**2)
        angle = math.atan2(dz, dx)
        
        # Create diagonal
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
        diag = bpy.context.active_object
        diag.name = f"Diagonal_{i}_{suffix}"
        diag.scale = (length, 0.2, 0.2)
        diag.rotation_euler = (0, angle, 0)
        bpy.ops.rigidbody.object_add()
        diag.rigid_body.type = 'PASSIVE'
        diagonals.append(diag)
    
    return top_chord, bottom_chord, verticals, diagonals, joint_positions_top, joint_positions_bottom

# 5. Create left and right trusses
left_truss = create_truss_side(-truss_offset_y, "L")
right_truss = create_truss_side(truss_offset_y, "R")

# 6. Add Fixed Constraints between connected members
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object2 = obj_b

# Connect verticals to chords at each joint
for i in range(num_segments + 1):
    # Left side
    add_fixed_constraint(left_truss[2][i], left_truss[0])  # vertical to top chord
    add_fixed_constraint(left_truss[2][i], left_truss[1])  # vertical to bottom chord
    # Right side
    add_fixed_constraint(right_truss[2][i], right_truss[0])
    add_fixed_constraint(right_truss[2][i], right_truss[1])

# Connect diagonals to appropriate joints (simplified: connect to nearest vertical)
for i in range(num_segments):
    # Left side
    add_fixed_constraint(left_truss[3][i], left_truss[2][i])  # diagonal to vertical i
    add_fixed_constraint(left_truss[3][i], left_truss[2][i+1])  # diagonal to vertical i+1
    # Right side
    add_fixed_constraint(right_truss[3][i], right_truss[2][i])
    add_fixed_constraint(right_truss[3][i], right_truss[2][i+1])

# Connect platform to top chords
add_fixed_constraint(platform, left_truss[0])
add_fixed_constraint(platform, right_truss[0])

# 7. Create Load (450kg sphere at midpoint)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(load_position_x, load_position_y, load_position_z))
load = bpy.context.active_object
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass_kg
load.rigid_body.type = 'ACTIVE'

# 8. Set up simulation world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

print("Truss bridge construction complete. Run simulation for", simulation_frames, "frames.")