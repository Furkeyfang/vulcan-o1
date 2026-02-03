import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube primitive (default 2×2×2)
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scale to achieve 3×1×2 dimensions
# Default cube vertices are at ±0.5, so scaling by (3,1,2) gives desired size
cube.scale = (1.5, 0.5, 1.0)  # Scale factors: 3/2, 1/2, 2/2
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (8.0, 7.0, 2.0)
cube.rotation_euler = (math.radians(45.0), 0.0, 0.0)  # 45° around X-axis

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'MESH'  # Use actual mesh for collision

# Optional: Set physics properties for predictable behavior
cube.rigid_body.mass = 1.0  # kg
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.3

# Ensure proper display
cube.display_type = 'SOLID'
bpy.context.view_layer.update()