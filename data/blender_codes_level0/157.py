import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with specified dimensions
# Note: bpy.ops.mesh.primitive_cube_add creates a 2x2x2 cube by default, so we scale
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "passive_cube"

# Apply dimensions: scale the default 2x2x2 cube to 2x5x1
# Since default cube is 2x2x2, scaling factor per axis is desired/2
cube.scale = (2.0/2.0, 5.0/2.0, 1.0/2.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-5.0, 0.0, 0.0)
cube.rotation_euler = (0.0, math.radians(25.0), 0.0)

# Add rigid body property and set to passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX for optimal performance
cube.rigid_body.collision_shape = 'BOX'