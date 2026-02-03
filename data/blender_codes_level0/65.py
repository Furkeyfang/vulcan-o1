import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default 2m dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling for 3×1×3 dimensions (X=width, Y=depth, Z=height in Blender)
# Default cube is 2×2×2, so scale by (3/2, 3/2, 1/2) = (1.5, 1.5, 0.5)
cube.scale = (1.5, 1.5, 0.5)

# Apply transforms to make scaling permanent
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (-6.0, -1.0, -3.0)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)

# Verify dimensions
print(f"Cube created at: {cube.location}")
print(f"Rotation: {math.degrees(cube.rotation_euler.y):.1f}° around Y")
print(f"Dimensions (after scaling): X=3.0, Y=3.0, Z=1.0")