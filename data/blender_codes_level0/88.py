import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube (default 2x2x2, but we will scale)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TaskCube"

# Scale to achieve 2x5x2 dimensions (since default size=1 gives a 2x2x2 cube, we adjust)
# The default cube with size=1 has vertices from -1 to 1, so total dimension is 2.
# To get width=2, height=5, depth=2, we set scale accordingly.
# Scale X = desired_width / default_width = 2 / 2 = 1.0
# Scale Y = desired_height / default_height = 5 / 2 = 2.5
# Scale Z = desired_depth / default_depth = 2 / 2 = 1.0
cube.scale = (1.0, 2.5, 1.0)

# Set location
cube.location = (-4.0, -2.0, 5.0)

# Set rotation (30 degrees around X-axis)
cube.rotation_euler[0] = math.radians(30.0)  # 30 degrees in radians

# Optionally, we can set the object to be a passive rigid body if physics is needed.
# For this static placement, we leave it without physics.
# If physics were required, we would add:
# bpy.ops.rigidbody.object_add()
# cube.rigid_body.type = 'PASSIVE'

# Update the scene
bpy.context.view_layer.update()