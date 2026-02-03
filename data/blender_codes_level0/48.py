import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube at origin (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Target_Cube"

# Scale to 3x3x3 (scale factor = desired/initial = 3/2 = 1.5)
cube.scale = (1.5, 1.5, 1.5)

# Apply scale transform to make it actual geometry
bpy.ops.object.transform_apply(scale=True)

# Set rotation (45° around Y axis)
cube.rotation_euler = (0, math.radians(45), 0)

# Set final position
cube.location = (2.0, 2.0, 2.0)

# Verify transformations
print(f"Cube created: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation (degrees): {[math.degrees(a) for a in cube.rotation_euler]}")