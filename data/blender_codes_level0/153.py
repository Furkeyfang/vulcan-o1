import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with base dimensions (Blender default cube is 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Set dimensions: scale from default 2m to desired dimensions
cube.scale.x = 1.0 / 2.0  # Target X=1, default=2 -> scale=0.5
cube.scale.y = 3.0 / 2.0  # Target Y=3, default=2 -> scale=1.5
cube.scale.z = 2.0 / 2.0  # Target Z=2, default=2 -> scale=1.0

# Apply scale to make dimensions explicit
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (6.0, 0.0, 1.0)

# Set rotation (45° around X-axis)
cube.rotation_euler = (math.radians(45.0), 0.0, 0.0)

# Add rigid body physics (passive)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'