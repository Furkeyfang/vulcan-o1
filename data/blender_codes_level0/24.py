import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube primitive (default 2×2×2)
bpy.ops.mesh.primitive_cube_add()
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling for 2×2×3 dimensions
cube.scale = (1.0, 1.0, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set rotation (90° around X-axis)
cube.rotation_euler = (math.radians(90), 0, 0)

# Set location
cube.location = (3.0, 3.0, 3.0)

# Apply rotation to mesh data
bpy.ops.object.transform_apply(rotation=True)

print(f"Cube '{cube.name}' created:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (Euler): {cube.rotation_euler}")