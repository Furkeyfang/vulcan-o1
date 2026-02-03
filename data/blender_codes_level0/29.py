import bpy
import math

# Clear existing mesh objects for a clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to desired dimensions: 2 (X), 1 (Y), 2 (Z)
# Default cube is 2x2x2, so scale factors are (1, 0.5, 1)
cube.scale = (1.0, 0.5, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation (convert degrees to radians)
cube.location = (4.0, 0.0, 4.0)
cube.rotation_euler = (0.0, math.radians(33.0), 0.0)

# Optional: Apply rotation for clean transforms
bpy.ops.object.transform_apply(rotation=True)

print(f"Cube '{cube.name}' created at {cube.location} with rotation {cube.rotation_euler}")