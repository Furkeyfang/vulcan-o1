import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "custom_cube"

# Apply scaling to achieve 1x3x5 dimensions
cube.scale = (0.5, 1.5, 2.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-7.0, 2.0, 2.0)
cube.rotation_euler = (0.0, math.radians(35.0), 0.0)

# Optionally, set display to wireframe to see dimensions clearly
cube.display_type = 'WIRE'