import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Apply scale transformation
cube.scale = (1.5, 0.5, 0.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set position and rotation
cube.location = (-3.0, 0.0, 0.0)
cube.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Add rigid body physics (passive)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX for accuracy
cube.rigid_body.collision_shape = 'BOX'