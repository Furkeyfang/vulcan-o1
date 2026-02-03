import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)

# Get the active object
cube = bpy.context.active_object
cube.name = "Rectangular_Prism"

# Apply scaling to achieve 4x1x1 dimensions
cube.scale = (2.0, 0.5, 0.5)

# Apply rotation (75° around Y-axis)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)

# Apply location
cube.location = (3.0, 0.0, -2.0)

# Apply transformations to make them intrinsic (clean object data)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)