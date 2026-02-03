import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Scale to achieve 1x4x1 dimensions
cube.scale = (0.5, 2.0, 0.5)  # (1/2, 4/2, 1/2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location
cube.location = (0.0, 8.0, 5.0)

# Apply 45° X-axis rotation
cube.rotation_euler.x = math.radians(45.0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0  # Default mass

# Verify final transform
print(f"Cube created at: {cube.location}")
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube rotation (degrees): {[math.degrees(r) for r in cube.rotation_euler]}")