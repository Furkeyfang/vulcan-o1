import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Set scale for dimensions (default 2m cube → scale by 1.5,0.5,1.5 for 3x1x3m)
cube.scale = (1.5, 0.5, 1.5)

# Apply transformations
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (-6.0, 0.0, -3.0)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Update viewport
bpy.context.view_layer.update()