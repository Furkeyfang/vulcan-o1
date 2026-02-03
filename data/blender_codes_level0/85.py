import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling for 3×3×2 dimensions
cube.scale = (1.5, 1.5, 1.0)  # X, Y, Z scale factors

# Apply 90° rotation around X-axis (convert degrees to radians)
rotation_rad = math.radians(90.0)
cube.rotation_euler = (rotation_rad, 0.0, 0.0)

# Apply translation to target location
cube.location = (5.0, -5.0, 0.0)

# Update transformations
bpy.context.view_layer.update()

# Verification output
print(f"Cube created at {cube.location}")
print(f"Dimensions (world): {cube.dimensions}")
print(f"Rotation (degrees): {tuple(math.degrees(r) for r in cube.rotation_euler)}")