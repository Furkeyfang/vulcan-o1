import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create unit cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply dimensions via scale (alternatively set dimensions directly)
cube.scale = (3.0, 3.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (9.0, 7.0, -2.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)  # 90° about X

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0  # Default mass (optional)