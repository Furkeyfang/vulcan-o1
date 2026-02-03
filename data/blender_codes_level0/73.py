import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply non-uniform scaling for 2x3x3 dimensions
# Default cube is 2x2x2, so scale factors: (2/2, 3/2, 3/2) = (1, 1.5, 1.5)
cube.scale = (1.0, 1.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (4.0, -4.0, 4.0)
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Verify transformations
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation (degrees): {[math.degrees(angle) for angle in cube.rotation_euler]}")