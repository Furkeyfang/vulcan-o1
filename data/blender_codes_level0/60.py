import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "3x2x4_Cube"

# Apply scaling to achieve 3x2x4 dimensions
cube.scale = (1.5, 1.0, 2.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-1.0, -1.0, -7.0)
cube.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Optional: Add rigid body for physics simulation
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 24.0  # Proportional to volume (3*2*4 = 24 m³)

# Verify dimensions
print(f"Object: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation (degrees): {math.degrees(cube.rotation_euler.y):.1f}°")