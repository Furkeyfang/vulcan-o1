import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a cube with initial size 1 (creates a 1x1x1 cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Scale to desired dimensions (5, 1, 3)
cube.scale = (5.0, 1.0, 3.0)

# Set location and rotation
cube.location = (-8.0, 0.0, 0.0)
cube.rotation_euler = (0.0, 0.0, math.radians(30.0))

# Apply transformations so scale and rotation are baked (clean for physics)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Add rigid body and set to passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'