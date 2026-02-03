import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube with initial size 2 (creates 2x2x2 cube)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to achieve 2x2x6 dimensions
# Default cube is 2x2x2, so Z must be scaled by 3 to get 6m height
cube.scale = (1.0, 1.0, 3.0)

# Apply the scale so dimensions are correct and rotation works properly
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (0.0, 4.0, -7.0)

# Set rotation: 20 degrees around Z-axis
cube.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Optional: Set origin to geometry center for clarity
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')