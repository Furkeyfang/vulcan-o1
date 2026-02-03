import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply scale to achieve 2x4x2 dimensions
cube.scale = (1.0, 2.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (5.0, 9.0, -9.0)
cube.rotation_euler = (0.0, math.radians(20.0), 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'