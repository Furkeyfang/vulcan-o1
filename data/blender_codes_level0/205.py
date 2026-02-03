import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with dimensions 2x2x2
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "passive_cube"

# Set location
cube.location = (6.0, 0.0, 6.0)

# Convert 60 degrees to radians and apply X rotation
cube.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Add rigid body physics as passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'