import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default 2x2x2 dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "cube_obstacle"

# Apply scaling to achieve 1x1x3 dimensions (default cube is 2x2x2)
# Scale factors = desired_dimension / 2.0
cube.scale = (0.5, 0.5, 1.5)

# Apply rotation and translation
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)
cube.location = (7.0, 0.0, 0.0)

# Apply transformations to make them direct object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX (default for cubes)
cube.rigid_body.collision_shape = 'BOX'