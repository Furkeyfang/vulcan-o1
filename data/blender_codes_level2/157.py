import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
cube_dim = 1.0
num_cubes = 15
column_height = 15.0
bottom_cube_z = 0.5
force_magnitude = 24525.0
force_location = (0.0, 0.0, 15.0)
simulation_frames = 100

# Create stacked cubes
cubes = []
for i in range(num_cubes):
    z_pos = bottom_cube_z + i * cube_dim
    bpy.ops.mesh.primitive_cube_add(size=cube_dim, location=(0, 0, z_pos))
    cube = bpy.context.active_object
    cube.name = f"Cube_{i+1}"
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    
    # Bottom cube is passive (fixed), others active
    if i == 0:
        cube.rigid_body.type = 'PASSIVE'
    else:
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = 100.0  # Arbitrary mass, high for stability
    
    cubes.append(cube)

# Add fixed constraints between adjacent cubes
for i in range(1, num_cubes):
    upper_cube = cubes[i]
    lower_cube = cubes[i-1]
    
    # Create empty object as constraint anchor
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Fixed_{i}"
    
    # Parent empty to upper cube (so it moves with it)
    constraint_empty.parent = upper_cube
    constraint_empty.matrix_parent_inverse = upper_cube.matrix_world.inverted()
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = upper_cube
    constraint.object2 = lower_cube

# Apply downward force at top of column
# Create force field (downward gravity-like force)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=force_location)
force_empty = bpy.context.active_object
force_empty.name = "Force_Field"
bpy.ops.object.forcefield_add()
force_field = force_empty.field
force_field.type = 'FORCE'
force_field.strength = -force_magnitude  # Negative for downward
force_field.use_max_distance = True
force_field.distance_max = 0.1  # Only affect top cube

# Parent force field to top cube to ensure it stays at top
force_empty.parent = cubes[-1]
force_empty.matrix_parent_inverse = cubes[-1].matrix_world.inverted()

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Optional: run simulation in headless (will be executed when rendering)
# bpy.ops.ptcache.bake_all(bake=True)