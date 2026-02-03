import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling to achieve 4×1×2 dimensions
cube.scale = (2.0, 0.5, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (1.0, 4.0, -4.0)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)

# Optional: Set visual properties
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)
cube.data.materials.append(mat)

print(f"Cube created at {cube.location} with rotation {math.degrees(cube.rotation_euler.y):.1f}°")
print(f"Dimensions: {cube.dimensions}")