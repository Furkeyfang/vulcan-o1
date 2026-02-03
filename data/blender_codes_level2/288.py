import bpy
import mathutils
from mathutils import Vector
import math

# ======================
# 1. CLEAR SCENE
# ======================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ======================
# 2. PARAMETERS
# ======================
# Towers
tower_width = 1.0
tower_depth = 1.0
tower_height = 10.0
tower_separation = 8.0
left_tower_x = -tower_separation / 2.0
right_tower_x = tower_separation / 2.0
tower_y = 0.0
tower_bottom_z = 0.0

# Beam
beam_length = 10.0
beam_width = 1.0
beam_thickness = 0.5
beam_x = 0.0
beam_y = 0.0
beam_z = tower_bottom_z + tower_height + beam_thickness / 2.0  # 10.25

# Platform
platform_size = 2.0
platform_thickness = 0.2
platform_x = 0.0
platform_y = 0.0
platform_z = beam_z - beam_thickness / 2.0 + platform_thickness / 2.0  # 10.1

# Cables
cable_radius = 0.1
cable_primitive_height = 8.0
platform_mass = 900.0
simulation_frames = 100

# ======================
# 3. CREATE GROUND PLANE
# ======================
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ======================
# 4. CREATE TOWERS
# ======================
def create_tower(x_pos, name):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, tower_y, tower_bottom_z + tower_height / 2.0))
    tower = bpy.context.active_object
    tower.name = name
    tower.scale = (tower_width, tower_depth, tower_height)
    bpy.ops.rigidbody.object_add()
    tower.rigid_body.type = 'ACTIVE'
    return tower

left_tower = create_tower(left_tower_x, "LeftTower")
right_tower = create_tower(right_tower_x, "RightTower")

# ======================
# 5. CREATE BEAM
# ======================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(beam_x, beam_y, beam_z))
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_length, beam_width, beam_thickness)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'

# ======================
# 6. CREATE PLATFORM
# ======================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(platform_x, platform_y, platform_z))
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (platform_size, platform_size, platform_thickness)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = platform_mass

# ======================
# 7. CREATE CABLES
# ======================
def create_cable(start_point, end_point, name):
    # Calculate vector between points
    vec = Vector(end_point) - Vector(start_point)
    distance = vec.length
    
    # Create cylinder at origin
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=cable_radius,
        depth=cable_primitive_height,
        location=(0, 0, 0)
    )
    cable = bpy.context.active_object
    cable.name = name
    
    # Scale to match distance
    scale_z = distance / cable_primitive_height
    cable.scale = (1.0, 1.0, scale_z)
    
    # Position at midpoint
    mid_point = (Vector(start_point) + Vector(end_point)) / 2.0
    cable.location = mid_point
    
    # Rotate to align with vector
    # Default cylinder points along local Z
    up_vec = Vector((0, 0, 1))
    rot_quat = up_vec.rotation_difference(vec)
    cable.rotation_mode = 'QUATERNION'
    cable.rotation_quaternion = rot_quat
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    cable.rigid_body.type = 'ACTIVE'
    return cable

# Tower corner coordinates (at Z=10)
tower_half = tower_width / 2.0
left_tower_corners = {
    'front_right': Vector((left_tower_x + tower_half, tower_half, tower_bottom_z + tower_height)),
    'front_left': Vector((left_tower_x - tower_half, tower_half, tower_bottom_z + tower_height)),
    'back_right': Vector((left_tower_x + tower_half, -tower_half, tower_bottom_z + tower_height)),
    'back_left': Vector((left_tower_x - tower_half, -tower_half, tower_bottom_z + tower_height))
}

right_tower_corners = {
    'front_right': Vector((right_tower_x + tower_half, tower_half, tower_bottom_z + tower_height)),
    'front_left': Vector((right_tower_x - tower_half, tower_half, tower_bottom_z + tower_height)),
    'back_right': Vector((right_tower_x + tower_half, -tower_half, tower_bottom_z + tower_height)),
    'back_left': Vector((right_tower_x - tower_half, -tower_half, tower_bottom_z + tower_height))
}

# Platform corner coordinates (at Z=platform_z)
platform_half = platform_size / 2.0
platform_corners = {
    'front_right': Vector((platform_half, platform_half, platform_z)),
    'front_left': Vector((-platform_half, platform_half, platform_z)),
    'back_right': Vector((platform_half, -platform_half, platform_z)),
    'back_left': Vector((-platform_half, -platform_half, platform_z))
}

# Create 4 cables: left tower to left platform corners, right tower to right platform corners
cables = []
cables.append(create_cable(
    left_tower_corners['front_left'],
    platform_corners['front_left'],
    "Cable_LeftFront"
))
cables.append(create_cable(
    left_tower_corners['back_left'],
    platform_corners['back_left'],
    "Cable_LeftBack"
))
cables.append(create_cable(
    right_tower_corners['front_right'],
    platform_corners['front_right'],
    "Cable_RightFront"
))
cables.append(create_cable(
    right_tower_corners['back_right'],
    platform_corners['back_right'],
    "Cable_RightBack"
))

# ======================
# 8. CREATE CONSTRAINTS
# ======================
def add_fixed_constraint(obj_a, obj_b):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    const = bpy.context.active_object
    const.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    const.location = (obj_a.location + obj_b.location) / 2.0
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj_a
    const.rigid_body_constraint.object2 = obj_b
    return const

# Towers to Ground
add_fixed_constraint(left_tower, ground)
add_fixed_constraint(right_tower, ground)

# Towers to Beam
add_fixed_constraint(left_tower, beam)
add_fixed_constraint(right_tower, beam)

# Platform to Beam
add_fixed_constraint(platform, beam)

# Cables to Towers and Platform
# Cable 0: LeftFront
add_fixed_constraint(cables[0], left_tower)
add_fixed_constraint(cables[0], platform)
# Cable 1: LeftBack
add_fixed_constraint(cables[1], left_tower)
add_fixed_constraint(cables[1], platform)
# Cable 2: RightFront
add_fixed_constraint(cables[2], right_tower)
add_fixed_constraint(cables[2], platform)
# Cable 3: RightBack
add_fixed_constraint(cables[3], right_tower)
add_fixed_constraint(cables[3], platform)

# ======================
# 9. SET SIMULATION
# ======================
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Double-tower cable-supported frame created successfully.")
print(f"Platform mass: {platform_mass} kg")
print(f"Simulation frames: {simulation_frames}")