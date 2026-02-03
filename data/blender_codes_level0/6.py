import bpy
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling to achieve 1x3x1 dimensions
cube.scale = (0.5, 1.5, 0.5)
bpy.ops.object.transform_apply(scale=True)

# Set rotation (90° about X-axis)
cube.rotation_euler = (radians(90.0), 0.0, 0.0)

# Set location
cube.location = (1.0, 0.0, -3.0)

# Optionally set object origin to geometry center for clarity
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')