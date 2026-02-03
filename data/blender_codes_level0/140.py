import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default dimensions (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Scale to achieve 5×2×1 dimensions
# Default cube has vertices at ±0.5 in all axes, so scaling factors are:
# X: 5.0/1.0 = 5.0, Y: 2.0/1.0 = 2.0, Z: 1.0/1.0 = 1.0
cube.scale = (5.0, 2.0, 1.0)

# Apply scale to make transformations clean
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set position and rotation
cube.location = (6.0, 7.0, 2.0)
cube.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Ensure proper display of dimensions
cube.show_bounds = True
cube.display_type = 'SOLID'