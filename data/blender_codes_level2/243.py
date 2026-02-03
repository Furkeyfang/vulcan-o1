import bpy
import math
from mathutils import Matrix, Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
base_dim = Vector((14.0, 8.0, 0.5))
wall_dim = Vector((14.0, 0.5, 4.0))
wall_y = 3.75
wall_z = 2.25
ridge_dim = Vector((14.0, 0.5, 0.5))
ridge_z = 4.5
slope_cross = Vector((0.5, 0.5))
upper_len = 3.5
upper_ang = math.radians(30)
lower_len = 1.662
lower_ang = math.radians(64.4)
brace_cross = Vector((0.5, 0.5))
load_dim = Vector((14.0, 8.0, 0.1))
load_mass = 1200.0
load_z = 5.05

# Helper function to create a cube with physics
def create_cube(name, location, scale, rigid_body_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_body_type
    return obj

# Helper function to create a rotated beam
def create_beam(name, start, end, cross_section, angle_deg, axis='X'):
    # Create cube at origin
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length is distance between start and end
    length = (end - start).length
    beam.scale = (cross_section.x, length, cross_section.y)
    
    # Rotate to align with vector
    vec = end - start
    if axis == 'X':
        # Rotate around X axis by angle
        beam.rotation_euler = (angle_deg, 0, 0)
    elif axis == 'Z':
        # Calculate rotation in XY plane
        angle_xy = math.atan2(vec.y, vec.x)
        beam.rotation_euler = (0, 0, angle_xy)
    
    # Move to midpoint
    midpoint = (start + end) / 2
    beam.location = midpoint
    
    # Add physics
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    return beam

# 1. Create Base
base = create_cube("Base", (0,0,0), base_dim)

# 2. Create Walls
left_wall = create_cube("Left_Wall", (0, -wall_y, wall_z), wall_dim)
right_wall = create_cube("Right_Wall", (0, wall_y, wall_z), wall_dim)

# 3. Create Central Ridge Beam
ridge = create_cube("Ridge", (0, 0, ridge_z), ridge_dim)

# 4. Create Truss Slopes (Right Side)
# Upper slope start (at ridge end)
upper_start = Vector((0, ridge_dim.y/2, ridge_z))
upper_end = Vector((
    0,
    upper_start.y + upper_len * math.cos(upper_ang),
    ridge_z - upper_len * math.sin(upper_ang)
))
upper_beam = create_beam("Upper_Slope_Right", upper_start, upper_end, slope_cross, upper_ang, 'X')

# Lower slope (adjusted to meet wall top)
lower_start = upper_end
lower_end = Vector((0, wall_y - wall_dim.y/2, ridge_z))  # Wall inner top
lower_beam = create_beam("Lower_Slope_Right", lower_start, lower_end, slope_cross, lower_ang, 'X')

# 5. Create Left Side (mirror)
upper_start_left = Vector((0, -ridge_dim.y/2, ridge_z))
upper_end_left = Vector((
    0,
    upper_start_left.y - upper_len * math.cos(upper_ang),
    ridge_z - upper_len * math.sin(upper_ang)
))
upper_beam_left = create_beam("Upper_Slope_Left", upper_start_left, upper_end_left, slope_cross, -upper_ang, 'X')

lower_start_left = upper_end_left
lower_end_left = Vector((0, -wall_y + wall_dim.y/2, ridge_z))
lower_beam_left = create_beam("Lower_Slope_Left", lower_start_left, lower_end_left, slope_cross, -lower_ang, 'X')

# 6. Create Diagonal Braces (Right side, from ridge to lower slope midpoint)
brace_start = Vector((0, ridge_dim.y/2, ridge_z))
brace_mid = (upper_end + lower_end) / 2
brace_end = Vector((0, brace_mid.y, brace_mid.z))
brace = create_beam("Diagonal_Brace_Right", brace_start, brace_end, brace_cross, 0, 'Z')

# Left side brace
brace_start_left = Vector((0, -ridge_dim.y/2, ridge_z))
brace_mid_left = (upper_end_left + lower_end_left) / 2
brace_end_left = Vector((0, brace_mid_left.y, brace_mid_left.z))
brace_left = create_beam("Diagonal_Brace_Left", brace_start_left, brace_end_left, brace_cross, 0, 'Z')

# 7. Create Load Plate
load = create_cube("Load", (0, 0, load_z), load_dim, 'ACTIVE')
load.rigid_body.mass = load_mass

# 8. Add Fixed Constraints between structural elements
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.name = f"Fix_{obj_a.name}_{obj_b.name}"
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj_a
    const.rigid_body_constraint.object2 = obj_b

# Connect walls to base
add_fixed_constraint(base, left_wall)
add_fixed_constraint(base, right_wall)

# Connect ridge to walls
add_fixed_constraint(left_wall, ridge)
add_fixed_constraint(right_wall, ridge)

# Connect slopes to ridge and walls
add_fixed_constraint(ridge, upper_beam)
add_fixed_constraint(ridge, upper_beam_left)
add_fixed_constraint(upper_beam, lower_beam)
add_fixed_constraint(upper_beam_left, lower_beam_left)
add_fixed_constraint(lower_beam, right_wall)
add_fixed_constraint(lower_beam_left, left_wall)

# Connect braces
add_fixed_constraint(brace, ridge)
add_fixed_constraint(brace, lower_beam)
add_fixed_constraint(brace_left, ridge)
add_fixed_constraint(brace_left, lower_beam_left)

# Set up simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100