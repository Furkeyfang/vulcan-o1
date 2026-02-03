import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
num_cubes = 15
cube_size = 1.0
tilt_angle_deg = 5.0
tilt_angle_rad = math.radians(tilt_angle_deg)
base_cube_center_z = 0.5
load_cube_size = 0.5
load_mass_kg = 400.0
load_cube_x = 15 * math.sin(tilt_angle_rad)
load_cube_z = 15 * math.cos(tilt_angle_rad) + 0.25
simulation_frames = 100
stability_threshold = 0.001

# Create tilted tower cubes
cubes = []
for i in range(num_cubes):
    # Calculate center position for this cube
    x_pos = (i + 0.5) * math.sin(tilt_angle_rad)
    z_pos = (i + 0.5) * math.cos(tilt_angle_rad)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(x_pos, 0, z_pos))
    cube = bpy.context.active_object
    cube.name = f"Cube_{i:02d}"
    
    # Rotate cube to align with tilt (around global origin)
    cube.rotation_euler = (0, tilt_angle_rad, 0)
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    if i == 0:
        cube.rigid_body.type = 'PASSIVE'  # Base cube fixed
    else:
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = 1.0  # Default mass
    
    cubes.append(cube)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=load_cube_size, location=(load_cube_x, 0, load_cube_z))
load_cube = bpy.context.active_object
load_cube.name = "Load_Cube"
load_cube.rotation_euler = (0, tilt_angle_rad, 0)
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass_kg
cubes.append(load_cube)

# Add fixed constraints between adjacent cubes
for i in range(len(cubes) - 1):
    bpy.ops.object.select_all(action='DESELECT')
    cubes[i+1].select_set(True)
    cubes[i].select_set(True)
    bpy.context.view_layer.objects.active = cubes[i]
    bpy.ops.rigidbody.connect()

# Set up scene for simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Optional: Bake simulation to verify stability
# Note: Headless mode can't use bpy.ops.ptcache.bake, but we can run simulation
# by advancing frames. For verification, we'd need to check positions after simulation.
# This code sets up the structure; actual simulation requires running Blender with
# --render-animation or scripting frame updates.