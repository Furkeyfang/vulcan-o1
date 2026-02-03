import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube (Blender default is 2x2x2, so scale by 0.5 for 1x1x1)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "active_cube"

# Set scale to 0.5 for 1m cube (since default 2m cube)
cube.scale = (0.5, 0.5, 0.5)

# Set location and rotation
cube.location = (2.0, 6.0, 2.0)
cube.rotation_euler = (math.radians(15.0), 0.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0

# Apply transforms to make scale and rotation explicit
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Optional: Set visual origin to geometry center
bpy.context.view_layer.objects.active = cube
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')