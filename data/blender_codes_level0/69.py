import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add a cube at the origin with default size (2m)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TaskCube"

# Set dimensions to 1x2x4 meters
cube.dimensions = (1.0, 2.0, 4.0)

# Set location and rotation
cube.location = (6.0, 1.0, -3.0)
cube.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Update mesh to apply transformations (optional, but ensures dimensions are correct)
bpy.context.view_layer.update()