import bpy
import math

# Clear existing mesh objects (optional, clean start)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with base dimensions of 2 (Blender default)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "passive_cube"

# Scale to achieve 4x1x1 dimensions (scale = desired / default)
# Default cube is 2x2x2, so scaling factor = desired_dimension / 2.0
cube.scale.x = 4.0 / 2.0  # Length
cube.scale.y = 1.0 / 2.0  # Width
cube.scale.z = 1.0 / 2.0  # Height

# Apply scale to make dimensions intrinsic
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (8.0, 0.0, -1.0)
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'