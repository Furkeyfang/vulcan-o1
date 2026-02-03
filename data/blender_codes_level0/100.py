import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube at origin
bpy.ops.mesh.primitive_cube_add()
cube = bpy.context.active_object
cube.name = "3x3x1_Cube"

# Apply transformations
cube.scale = (1.5, 1.5, 0.5)
cube.location = (9.0, 0.0, -2.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Apply scale to make dimensions explicit in mesh data
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Verify dimensions
print(f"Object location: {cube.location}")
print(f"Object rotation: {cube.rotation_euler}")
print(f"Object dimensions: {cube.dimensions}")