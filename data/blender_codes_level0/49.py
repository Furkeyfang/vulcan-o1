import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2)

# Get reference to the cube
cube = bpy.context.active_object
cube.name = "target_cube"

# Apply scaling to achieve 1x1x5 dimensions
# Default cube is 2x2x2, so scale factors = desired/2
cube.scale = (0.5, 0.5, 2.5)

# Apply scale transformation to make it permanent
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (0.0, 2.0, -6.0)

# Set rotation (90° around Z-axis)
cube.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Update scene
bpy.context.view_layer.update()

# Optional: Add visual materials for clarity
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # Blue color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

print(f"Cube created at {cube.location} with rotation {cube.rotation_euler}")
print(f"Dimensions: {cube.dimensions}")