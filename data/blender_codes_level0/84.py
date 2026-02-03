import bpy
import math

# Clear existing objects in the scene (optional, for clean start)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Cube"

# Scale to desired dimensions (1, 4, 3)
cube.scale = (0.5, 2.0, 1.5)

# Apply rotation: 20 degrees around Z-axis (convert to radians)
rotation_rad = math.radians(20.0)
cube.rotation_euler = (0, 0, rotation_rad)

# Set location
cube.location = (-1.0, 7.0, -3.0)

# Update the mesh to apply transformations (optional, for clarity)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)