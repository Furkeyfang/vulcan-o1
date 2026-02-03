import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create large passive cube (3x3x1)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.5))
large_cube = bpy.context.active_object
large_cube.name = "large_cube"
large_cube.scale = (1.5, 1.5, 0.5)  # Scale default 2m cube to 3x3x1
bpy.ops.rigidbody.object_add()
large_cube.rigid_body.type = 'PASSIVE'

# Create small active cube (1x1x1) with rotation
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(1.5, 1.0, 0.5))
small_cube = bpy.context.active_object
small_cube.name = "small_cube"
small_cube.scale = (0.5, 0.5, 0.5)  # Scale default 2m cube to 1x1x1
small_cube.rotation_euler = (0.0, math.radians(45.0), 0.0)
bpy.ops.rigidbody.object_add()
small_cube.rigid_body.type = 'ACTIVE'

# Set rigid body properties for realism
small_cube.rigid_body.mass = 1.0
small_cube.rigid_body.friction = 0.5
small_cube.rigid_body.restitution = 0.2

# Ensure proper viewport display
bpy.context.view_layer.update()