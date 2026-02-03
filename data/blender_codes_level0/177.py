import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply scale to achieve 1x3x5 dimensions
cube.scale = (0.5, 1.5, 2.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-7.0, 0.0, 2.0)
cube.rotation_euler = (0.0, math.radians(35.0), 0.0)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set display to show rigid body
bpy.context.space_data.shading.type = 'SOLID'
bpy.context.space_data.shading.show_rigidbody = True

print(f"Created passive cube '{cube.name}' at {cube.location} with rotation {cube.rotation_euler}")