import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add a default cube (2x2x2) at origin
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling to achieve 1x1x4 dimensions
cube.scale = (0.5, 0.5, 2.0)

# Apply rotation: 90 degrees around Z-axis
cube.rotation_euler = (0, 0, math.radians(90))

# Apply translation to final location
cube.location = (2.0, 1.0, 1.0)

# Update the object's transformation
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Verify dimensions (optional)
dimensions = cube.dimensions
print(f"Cube dimensions: {dimensions.x:.2f} x {dimensions.y:.2f} x {dimensions.z:.2f}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation (Z): {math.degrees(cube.rotation_euler.z):.1f}°")