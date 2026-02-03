import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube (default 2×2×2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to achieve 2×3×2 dimensions
# Default cube vertices are from -1 to 1, so scaling factor = dimension/2
cube.scale = (1.0, 1.5, 1.0)  # (2/2, 3/2, 2/2)

# Apply scale to transform
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-3.0, -3.0, 3.0)
cube.rotation_euler = (math.radians(35.0), 0.0, 0.0)

# Verify dimensions
dimensions = cube.dimensions
print(f"Cube created at {cube.location}")
print(f"Dimensions (XYZ): {dimensions.x:.3f}, {dimensions.y:.3f}, {dimensions.z:.3f}")
print(f"Rotation (radians): {cube.rotation_euler.x:.3f}")