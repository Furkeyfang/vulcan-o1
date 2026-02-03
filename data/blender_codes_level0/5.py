import bpy
import math

# Clear existing objects (optional, for a clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a default cube (1x1x1)
bpy.ops.mesh.primitive_cube_add(size=1.0)

# Get the active object (the cube we just created)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to achieve 3x1x1 dimensions
# Default cube has vertices at ±0.5 on each axis. Scaling by (3,1,1) yields desired size.
cube.scale = (3.0, 1.0, 1.0)

# Apply the scale to make it the object's base geometry
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set the location
cube.location = (-4.0, 1.0, 0.0)

# Set the rotation (15 degrees around Y-axis)
# Convert degrees to radians
rotation_radians = math.radians(15.0)
cube.rotation_euler = (0.0, rotation_radians, 0.0)

# Apply the rotation to the object's data
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Optional: Set object display to see edges clearly
cube.display_type = 'SOLID'