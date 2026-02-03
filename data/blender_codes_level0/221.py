import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with specified dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply dimensions (scale from unit cube)
cube.scale = (2.0, 2.0, 5.0)

# Set location and rotation
cube.location = (1.0, 0.0, -9.0)
cube.rotation_euler = (0.0, 0.0, math.radians(30.0))

# Apply transforms to make scale (1,1,1) with actual dimensions
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX for accuracy
cube.rigid_body.collision_shape = 'BOX'

print(f"Created {cube.name} at {cube.location} with rotation {cube.rotation_euler}")