import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Scale to achieve 3x3x2 dimensions (default cube is 2x2x2)
cube.scale = (1.5, 1.5, 1.0)

# Apply scale to avoid issues with physics
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (5.0, 0.0, 0.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Add rigid body physics, set to passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'