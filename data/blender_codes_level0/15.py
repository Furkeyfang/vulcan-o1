import bpy
import math
from mathutils import Vector, Euler

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default Blender dimensions (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling to achieve 2x3x1 dimensions
# Default Blender cube has vertices at ±0.5 in local space
# Scaling factor = desired_dimension / default_dimension
scale_x = 2.0 / 1.0  # Default cube size is 1.0 when created with size=1.0
scale_y = 3.0 / 1.0
scale_z = 1.0 / 1.0
cube.scale = (scale_x, scale_y, scale_z)

# Apply rotation (35° around Y-axis)
rotation_rad = math.radians(35.0)
cube.rotation_euler = Euler((0.0, rotation_rad, 0.0), 'XYZ')

# Set location
cube.location = Vector((-5.0, 0.0, 2.0))

# Apply transformations to make them permanent in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Verify final dimensions
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation: {math.degrees(cube.rotation_euler.y)}°")

# Optional: Add visual differentiation
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # Blue color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)