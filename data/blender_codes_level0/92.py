import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with correct dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0)  # Start with unit cube
cube = bpy.context.active_object
cube.name = "TargetCube"

# Set dimensions: 3(X) × 2(Z) × 5(Y) in Blender axes
# Blender uses X(width), Y(depth), Z(height)
cube.dimensions = (3.0, 5.0, 2.0)

# Set location
cube.location = (4.0, 2.0, 7.0)

# Apply 45° rotation around Y-axis
cube.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Apply transformations to make them permanent in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Verify final properties
print(f"Cube created:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {cube.rotation_euler}")