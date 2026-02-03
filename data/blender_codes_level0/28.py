import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)

# Get the active object
cube = bpy.context.active_object
cube.name = "Placed_Cube"

# Apply scaling to achieve 1x5x1 dimensions
# Default cube is 2x2x2, so scale factors are desired/2
cube.scale = (0.5, 2.5, 0.5)

# Apply rotation: 90 degrees around Z-axis
cube.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Set location
cube.location = (2.0, -5.0, 2.0)

# Apply transforms to make scale and rotation permanent in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Verify final dimensions
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation (Z): {math.degrees(cube.rotation_euler.z)}°")