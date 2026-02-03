import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a default cube (2m x 2m x 2m)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to achieve dimensions 2m (X) x 1m (Y) x 3m (Z)
cube.scale = (1.0, 0.5, 1.5)

# Apply scale to make dimensions explicit in mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-2.0, -1.0, 4.0)
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)