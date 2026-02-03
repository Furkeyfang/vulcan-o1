import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a default cube (initially 2m x 2m x 2m)
bpy.ops.mesh.primitive_cube_add()

cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Set dimensions to 1x1x3 (scaling from default 2x2x2)
cube.dimensions = (1.0, 1.0, 3.0)

# Apply location and rotation
cube.location = (-9.0, 0.0, 0.0)
cube.rotation_euler.x = math.radians(60.0)

# Add rigid body and set to passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'