import bpy
import math
from mathutils import Matrix, Euler

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)  # Center at half-height
seg_count = 10
seg_dim = (0.5, 0.5, 1.0)
seg_gap = 1.0
beam_dim = (0.2, 0.2, 1.414)
beam_angle = math.radians(45.0)
top_dim = (2.0, 2.0, 0.5)
top_z = 10.25
load_mass = 1200.0
sim_frames = 100

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.mass = 1000.0  # Heavy base

# Create vertical segments
segments = []
for i in range(seg_count):
    z_pos = base_loc[2] + base_dim[2]/2 + i * seg_gap + seg_dim[2]/2
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, z_pos))
    seg = bpy.context.active_object
    seg.name = f"VerticalSegment_{i:02d}"
    seg.scale = seg_dim
    bpy.ops.rigidbody.object_add()
    seg.rigid_body.type = 'PASSIVE'
    segments.append(seg)

# Create cross-bracing at each joint (9 joints between 10 segments)
braces = []
for joint in range(seg_count - 1):
    lower_seg = segments[joint]
    upper_seg = segments[joint + 1]
    joint_z = base_loc[2] + base_dim[2]/2 + joint * seg_gap + seg_dim[2]
    
    # Four diagonal beams per joint
    for dir_x, dir_y, brace_name in [(1, 1, "A"), (-1, 1, "B"), (1, -1, "C"), (-1, -1, "D")]:
        # Beam position: midpoint between connected corners
        offset = seg_dim[0]/2
        pos_x = dir_x * offset/2
        pos_y = dir_y * offset/2
        pos_z = joint_z
        
        # Create beam
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pos_x, pos_y, pos_z))
        beam = bpy.context.active_object
        beam.name = f"CrossBrace_J{joint:02d}_{brace_name}"
        beam.scale = beam_dim
        
        # Rotate 45° in appropriate plane
        if abs(dir_x) == 1 and abs(dir_y) == 1:
            # Diagonal in both X and Y
            rot_matrix = Matrix.Rotation(beam_angle, 4, 'X' if dir_x*dir_y > 0 else 'Y')
            beam.matrix_world @= rot_matrix
            # Additional rotation for 3D diagonal
            beam.rotation_euler.z = math.radians(45 * dir_x)
        
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        braces.append(beam)

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, top_z))
top = bpy.context.active_object
top.name = "TopPlatform"
top.scale = top_dim
bpy.ops.rigidbody.object_add()
top.rigid_body.type = 'ACTIVE'
top.rigid_body.mass = load_mass
top.rigid_body.collision_shape = 'BOX'

# Apply fixed constraints
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object2 = obj_b

# Chain constraints: base -> segment0 -> segment1 -> ... -> segment9 -> top
add_fixed_constraint(base, segments[0])
for i in range(seg_count - 1):
    add_fixed_constraint(segments[i], segments[i + 1])
add_fixed_constraint(segments[-1], top)

# Connect braces to segments (each brace connects to lower and upper segment at joint)
brace_idx = 0
for joint in range(seg_count - 1):
    lower = segments[joint]
    upper = segments[joint + 1]
    for _ in range(4):  # Four braces per joint
        brace = braces[brace_idx]
        add_fixed_constraint(brace, lower)
        add_fixed_constraint(brace, upper)
        brace_idx += 1

# Setup physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

# Ensure all objects have proper collision margins
for obj in bpy.context.scene.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

print(f"Tower constructed: {seg_count} segments, {len(braces)} cross-braces, load = {load_mass} kg")