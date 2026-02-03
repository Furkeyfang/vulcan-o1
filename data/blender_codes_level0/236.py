import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2)

# Get reference
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scale transformation to achieve 3x3x2 dimensions
cube.scale = (1.5, 1.5, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-9.0, 8.0, 3.0)
cube.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
# Optionally set mass (default is 10.0 kg)
cube.rigid_body.mass = 10.0

# Verify final dimensions
print(f"Cube created:")
print(f"  Location: {cube.location}")
print(f"  Rotation: {cube.rotation_euler}")
print(f"  Scale: {cube.scale}")
print(f"  Dimensions: {cube.dimensions}")