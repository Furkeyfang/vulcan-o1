import bpy
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to 3x2x2 dimensions
cube.scale = (1.5, 1.0, 1.0)
# Apply scale to transform actual mesh geometry
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-2.0, 2.0, -5.0)
cube.rotation_euler = (0, 0, radians(15.0))

# Optional: Add a passive rigid body for future physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'