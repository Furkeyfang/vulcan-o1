import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
cube_count = 18
cube_size = 1.0
cube_height = 1.0
base_cube_center_z = 0.5
platform_dim = (0.5, 0.5, 0.1)
platform_mass = 180.0
platform_center_z = 18.05
constraint_type = 'FIXED'
gravity_z = -9.81

# Set scene gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, gravity_z)

# Create list to store cube objects
cubes = []

# Create vertical stack of cubes
for i in range(cube_count):
    # Calculate Z position: (i * cube_height) + base_cube_center_z
    cube_z = (i * cube_height) + base_cube_center_z
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(0, 0, cube_z))
    cube = bpy.context.active_object
    cube.name = f"Cube_{i+1}"
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    
    # First cube is passive (base), others active
    if i == 0:
        cube.rigid_body.type = 'PASSIVE'
    else:
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = cube_size**3  # 1m³ = 1000kg default density
    
    cubes.append(cube)

# Create fixed constraints between consecutive cubes
for i in range(1, cube_count):
    parent_cube = cubes[i-1]
    child_cube = cubes[i]
    
    # Create constraint
    bpy.ops.object.select_all(action='DESELECT')
    child_cube.select_set(True)
    bpy.context.view_layer.objects.active = child_cube
    bpy.ops.rigidbody.constraint_add()
    
    # Configure constraint
    constraint = child_cube.rigid_body_constraint
    constraint.type = constraint_type
    constraint.object1 = parent_cube
    constraint.object2 = child_cube
    
    # Set constraint location at the connection point (top of parent)
    connection_z = (i * cube_height)  # Exactly at the interface
    constraint.location = (0, 0, connection_z)

# Create load platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, platform_center_z))
platform = bpy.context.active_object
platform.name = "Load_Platform"
platform.scale = platform_dim

# Add rigid body to platform
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = platform_mass

# Create fixed constraint between top cube and platform
bpy.ops.object.select_all(action='DESELECT')
platform.select_set(True)
bpy.context.view_layer.objects.active = platform
bpy.ops.rigidbody.constraint_add()

constraint = platform.rigid_body_constraint
constraint.type = constraint_type
constraint.object1 = cubes[-1]  # Top cube
constraint.object2 = platform

# Constraint location at the connection (top of mast)
constraint.location = (0, 0, cube_count * cube_height)  # Z = 18m

# Configure simulation settings for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Select all for visualization
bpy.ops.object.select_all(action='SELECT')