import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default 2×2×2 dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scale to achieve 4×3×2 dimensions
# Default cube vertices at ±1, so scale by (4/2, 3/2, 2/2) = (2.0, 1.5, 1.0)
cube.scale = (2.0, 1.5, 1.0)

# Apply rotation (35° around X-axis)
rotation_rad = math.radians(35.0)
cube.rotation_euler = (rotation_rad, 0.0, 0.0)

# Apply location
cube.location = (-2.0, 8.0, 1.0)

# Apply transforms to make these the object's base transforms
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Verify final properties
print(f"Cube created:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (Euler): {cube.rotation_euler}")