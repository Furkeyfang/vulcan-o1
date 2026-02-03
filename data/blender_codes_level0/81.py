import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Target_Cube"

# Apply scaling for 2×1×5 dimensions
cube.scale = (1.0, 0.5, 2.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-2.0, -6.0, -2.0)
cube.rotation_euler = (0.0, 0.0, math.radians(45.0))
bpy.ops.object.transform_apply(rotation=True)

# Verify dimensions
print(f"Created: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation (Z): {math.degrees(cube.rotation_euler.z):.1f}°")