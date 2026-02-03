import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with specified dimensions
# Default cube in Blender is 2x2x2, so we'll scale accordingly
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "RotatedCube"

# Set dimensions (scale from default 2x2x2 cube)
cube.scale.x = 0.5  # 1.0 / 2.0
cube.scale.y = 1.5  # 3.0 / 2.0
cube.scale.z = 1.0  # 2.0 / 2.0

# Apply scale to make dimensions permanent
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location.x = 6.0
cube.location.y = -2.0
cube.location.z = 1.0

# Set rotation (45° around X-axis)
cube.rotation_euler.x = math.radians(45.0)
cube.rotation_euler.y = 0.0
cube.rotation_euler.z = 0.0

# Add visual verification by setting material
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

print(f"Cube created: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation (degrees): ({math.degrees(cube.rotation_euler.x):.1f}, {math.degrees(cube.rotation_euler.y):.1f}, {math.degrees(cube.rotation_euler.z):.1f})")