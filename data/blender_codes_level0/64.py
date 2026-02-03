import bpy
import math
from mathutils import Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with specified dimensions
# Blender's default cube is 2x2x2, so we need to scale it
bpy.ops.mesh.primitive_cube_add(size=2.0)  # Size is the overall dimension
cube = bpy.context.active_object
cube.name = "Cube_2x4x2"

# Apply scaling to achieve 2x4x2 dimensions
# Since default cube is 2x2x2, scaling factors are: (2/2, 4/2, 2/2) = (1, 2, 1)
cube.scale = (1.0, 2.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (5.0, 0.0, -5.0)

# Set rotation (20 degrees around X-axis)
rotation_rad = math.radians(20.0)
cube.rotation_euler = Euler((rotation_rad, 0.0, 0.0), 'XYZ')

# Apply rotation to make it permanent
bpy.ops.object.transform_apply(rotation=True)

# Alternative approach: Create with correct dimensions directly
# bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5, 0, -5))
# cube = bpy.context.active_object
# cube.scale = (1.0, 2.0, 1.0)  # Results in 2x4x2 dimensions
# cube.rotation_euler = Euler((math.radians(20), 0, 0), 'XYZ')
# bpy.ops.object.transform_apply(scale=True, rotation=True)

print(f"Cube created at {cube.location} with dimensions {cube.dimensions}")