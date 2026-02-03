import bpy
import math

# Clear existing objects (optional)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2m³ at origin)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Set scale to achieve 4×3×2 dimensions
# Default cube is 2m in each dimension, so scale factors:
# X: 4.0/2.0 = 2.0, Y: 3.0/2.0 = 1.5, Z: 2.0/2.0 = 1.0
cube.scale = (2.0, 1.5, 1.0)

# Apply scale to make dimensions permanent
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-2.0, 0.0, 1.0)
cube.rotation_euler = (math.radians(35.0), 0.0, 0.0)

# Add rigid body physics as PASSIVE
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX for accuracy
cube.rigid_body.collision_shape = 'BOX'

print(f"Created passive cube:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {[math.degrees(angle) for angle in cube.rotation_euler]}")