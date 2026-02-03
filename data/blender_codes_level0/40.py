import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default dimensions (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)

# Get reference to the cube
cube = bpy.context.active_object
cube.name = "cube_5x2x1"

# Apply scaling to achieve 5x2x1 dimensions
# Default cube is 2m per side, so scale factors = desired/2
scale_x = 5.0 / 2.0
scale_y = 2.0 / 2.0
scale_z = 1.0 / 2.0
cube.scale = (scale_x, scale_y, scale_z)

# Apply scale transform to make dimensions permanent
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location
cube.location = (6.0, 2.0, 2.0)

# Set rotation: 20 degrees around global Z-axis
rotation_angle_rad = math.radians(20.0)
cube.rotation_euler = (0.0, 0.0, rotation_angle_rad)

# Apply rotation transform
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Verify final transform
print(f"Cube created: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation (Euler): {cube.rotation_euler}")

# Optional: Add material for visibility
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)