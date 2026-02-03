import bpy
from math import radians

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Scale to achieve 1x4x1 dimensions
cube.scale = (0.5, 2.0, 0.5)

# Apply scale to mesh data for accurate physics
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (0.0, 0.0, 6.0)
cube.rotation_euler = (0.0, radians(60.0), 0.0)

# Add rigid body and set to passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'