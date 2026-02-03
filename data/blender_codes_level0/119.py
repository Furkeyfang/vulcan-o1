import bpy
import math

# Clear existing objects (optional, ensures clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Scale to achieve 2×2×1 dimensions (default cube is 2×2×2)
# Scaling factors: desired / default = (2/2, 2/2, 1/2) = (1, 1, 0.5)
cube.scale = (1.0, 1.0, 0.5)

# Apply scale to make dimensions explicit in mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-1.0, 0.0, -1.0)
cube.rotation_euler.x = math.radians(25.0)  # 25° about X-axis

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set mass high for stability
cube.rigid_body.mass = 100.0

print(f"Created passive cube:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (degrees): {math.degrees(cube.rotation_euler.x)}° about X")