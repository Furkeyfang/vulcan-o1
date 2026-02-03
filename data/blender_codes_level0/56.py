import bpy
import math

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the cube with specified dimensions
# Blender's default cube is 2x2x2, so we scale by half the desired dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "PlacedCube"

# Set the dimensions directly (more accurate than scaling)
cube.dimensions = (4.0, 1.0, 3.0)

# Apply the scale to make dimensions permanent and avoid distortion
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (0.0, 3.0, 6.0)
cube.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Optional: Add a passive rigid body for potential physics scenes
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

print(f"Cube '{cube.name}' created at {cube.location} with rotation {cube.rotation_euler}")