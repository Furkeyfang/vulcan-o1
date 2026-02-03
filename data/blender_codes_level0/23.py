import bpy
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "scaled_cube"

# Apply scaling to achieve 1x4x1 dimensions
cube.scale = (0.5, 2.0, 0.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (0.0, -4.0, 0.0)
cube.rotation_euler = (0.0, radians(60.0), 0.0)

# Optional: Visual confirmation
print(f"Cube created: {cube.name}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (degrees): {cube.rotation_euler.y * 180 / 3.1415926535}")