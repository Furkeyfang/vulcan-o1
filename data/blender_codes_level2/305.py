import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
n_levels = 10
base_side = 10.0
cube_size = 1.0
level_height = 1.0
load_mass = 900.0
top_load_pos = (0.0, 0.0, 10.5)
frame_cube_mass = 2500.0
gravity = -9.81
sim_frames = 500

# Store cube objects per level for constraint creation
level_cubes = [[] for _ in range(n_levels)]

# Create pyramid levels
for level in range(n_levels):
    side = base_side - level  # side length in meters
    z_base = level * level_height  # bottom Z of this level
    z_center = z_base + cube_size/2.0
    
    if side == 1.0:
        # Top level: single cube
        bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(0,0,z_center))
        cube = bpy.context.active_object
        cube.name = f"Level_{level}_Cube"
        level_cubes[level].append(cube)
    else:
        # Create frame: perimeter of cubes
        half = side/2.0
        # Positions for cube centers along perimeter
        positions = []
        # Bottom row (y = -half + 0.5)
        for x in range(int(side)):
            x_pos = -half + 0.5 + x
            positions.append((x_pos, -half + 0.5, z_center))
        # Top row (y = half - 0.5)
        for x in range(int(side)):
            x_pos = -half + 0.5 + x
            positions.append((x_pos, half - 0.5, z_center))
        # Left column (x = -half + 0.5), exclude corners
        for y in range(1, int(side)-1):
            y_pos = -half + 0.5 + y
            positions.append((-half + 0.5, y_pos, z_center))
        # Right column (x = half - 0.5), exclude corners
        for y in range(1, int(side)-1):
            y_pos = -half + 0.5 + y
            positions.append((half - 0.5, y_pos, z_center))
        
        # Create cubes at these positions
        for idx, pos in enumerate(positions):
            bpy.ops.mesh.primitive_cube_add(size=cube_size, location=pos)
            cube = bpy.context.active_object
            cube.name = f"Level_{level}_Cube_{idx}"
            level_cubes[level].append(cube)

# Add rigid body physics to all frame cubes (PASSIVE)
for level in range(n_levels):
    for cube in level_cubes[level]:
        bpy.ops.rigidbody.object_add()
        cube.rigid_body.type = 'PASSIVE'
        cube.rigid_body.mass = frame_cube_mass
        cube.rigid_body.collision_shape = 'BOX'

# Create fixed constraints within each level
for level in range(n_levels):
    cubes = level_cubes[level]
    for i, cube1 in enumerate(cubes):
        for j, cube2 in enumerate(cubes[i+1:], start=i+1):
            # Check if cubes are adjacent (distance ~1.0)
            dist = (Vector(cube1.location) - Vector(cube2.location)).length
            if abs(dist - cube_size) < 0.01:  # adjacent
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=cube1.location)
                empty = bpy.context.active_object
                empty.name = f"Constraint_L{level}_{i}_{j}"
                bpy.ops.rigidbody.constraint_add()
                constraint = empty.rigid_body_constraint
                constraint.type = 'FIXED'
                constraint.object1 = cube1
                constraint.object2 = cube2

# Create fixed constraints between adjacent levels
for level in range(1, n_levels):
    upper_cubes = level_cubes[level]
    lower_cubes = level_cubes[level-1]
    for upper in upper_cubes:
        for lower in lower_cubes:
            # Check vertical projection distance
            horiz_dist = math.sqrt((upper.location.x - lower.location.x)**2 + 
                                 (upper.location.y - lower.location.y)**2)
            if horiz_dist < cube_size:  # overlapping vertically
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=upper.location)
                empty = bpy.context.active_object
                empty.name = f"Constraint_L{level}_to_L{level-1}"
                bpy.ops.rigidbody.constraint_add()
                constraint = empty.rigid_body_constraint
                constraint.type = 'FIXED'
                constraint.object1 = upper
                constraint.object2 = lower

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=cube_size, location=top_load_pos)
load_cube = bpy.context.active_object
load_cube.name = "Load_Cube"
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass
load_cube.rigid_body.collision_shape = 'BOX'

# Fix bottom level to ground (already PASSIVE)
# Ensure rigid body world exists
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.gravity[2] = gravity

# Set simulation frames
bpy.context.scene.frame_end = sim_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)