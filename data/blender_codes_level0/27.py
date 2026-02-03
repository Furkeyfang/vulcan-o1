import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to achieve 3x1x2 dimensions
# Default cube is 2m per side, so scale factors = desired/2
cube.scale = (3.0/2.0, 1.0/2.0, 2.0/2.0)  # (1.5, 0.5, 1.0)

# Apply scale to make it permanent (avoids distortion during rotation)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location
cube.location = (-3.0, 1.0, 5.0)

# Set rotation: 10° around X-axis
rotation_rad = math.radians(10.0)
cube.rotation_euler = (rotation_rad, 0.0, 0.0)

# Apply rotation to make it permanent
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Verify final transform
print(f"Final Location: {cube.location}")
print(f"Final Dimensions: {cube.dimensions}")
print(f"Final Rotation (Euler): {cube.rotation_euler}")
print(f"X-axis Rotation: {math.degrees(cube.rotation_euler.x):.2f}°")

# Optional: Add visual materials
mat = bpy.data.materials.new(name="CubeMaterial")
mat.use_nodes = True
cube.data.materials.append(mat)