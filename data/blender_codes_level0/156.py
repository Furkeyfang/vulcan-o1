import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with correct dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Scale to target dimensions (4×1×3) from default 2×2×2
cube.scale = (2.0, 0.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (0.0, 6.0, 6.0)
cube.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Configure as active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0  # Explicitly set mass (default)
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.1

print(f"Created {cube.name} with:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {cube.rotation_euler}")