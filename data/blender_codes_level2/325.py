import bpy
import math

# 1. Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Parameters from summary
span_x = 8.0
span_y = 8.0
grid_count = 5
cube_size = 0.2
z_center = 1.5
z_corner = 0.5
z_edge = 1.0
load_mass_kg = 900.0
gravity = 9.81
total_force_N = load_mass_kg * gravity
central_cubes_count = 9
force_per_cube_N = total_force_N / central_cubes_count
simulation_frames = 100
support_indices = [(0,0), (0,4), (4,0), (4,4)]
central_indices = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)]

# 3. Create grid of cubes
cubes = []
spacing_x = span_x / (grid_count - 1)
spacing_y = span_y / (grid_count - 1)
for i in range(grid_count):
    row = []
    for j in range(grid_count):
        # Grid coordinates centered at (0,0)
        x = (i - (grid_count-1)/2) * spacing_x
        y = (j - (grid_count-1)/2) * spacing_y
        
        # Parabolic Z: z = 0.5 + (1.0 - (x²+y²)/32)
        z = z_corner + (1.0 - (x**2 + y**2) / (span_x**2/2)) * (z_center - z_corner)
        
        # Create cube
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z))
        cube = bpy.context.active_object
        cube.scale = (cube_size, cube_size, cube_size)
        
        # Add rigid body
        bpy.ops.rigidbody.object_add()
        if (i,j) in support_indices:
            cube.rigid_body.type = 'PASSIVE'  # Fixed supports
        else:
            cube.rigid_body.type = 'ACTIVE'
            cube.rigid_body.collision_margin = 0.001
        
        row.append(cube)
    cubes.append(row)

# 4. Create fixed constraints between adjacent cubes
for i in range(grid_count):
    for j in range(grid_count):
        current = cubes[i][j]
        # Right neighbor (X+)
        if i+1 < grid_count:
            neighbor = cubes[i+1][j]
            bpy.ops.object.select_all(action='DESELECT')
            current.select_set(True)
            neighbor.select_set(True)
            bpy.context.view_layer.objects.active = current
            bpy.ops.rigidbody.connect()
            constraint = bpy.context.active_object
            constraint.rigid_body_constraint.type = 'FIXED'
        # Up neighbor (Y+)
        if j+1 < grid_count:
            neighbor = cubes[i][j+1]
            bpy.ops.object.select_all(action='DESELECT')
            current.select_set(True)
            neighbor.select_set(True)
            bpy.context.view_layer.objects.active = current
            bpy.ops.rigidbody.connect()
            constraint = bpy.context.active_object
            constraint.rigid_body_constraint.type = 'FIXED'

# 5. Apply forces to central cubes
for i, j in central_indices:
    cube = cubes[i][j]
    # Apply downward force in global Z
    cube.rigid_body.force = (0.0, 0.0, -force_per_cube_N)

# 6. Set simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -gravity)

# 7. Enable rigid body simulation
bpy.context.scene.rigidbody_world.enabled = True