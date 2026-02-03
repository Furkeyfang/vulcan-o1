import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with base dimensions (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply scaling for 2×3×3 dimensions
cube.scale = (1.0, 1.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set final location and rotation
cube.location = (3.0, 0.0, -7.0)
cube.rotation_euler = (0.0, math.radians(90.0), 0.0)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'