import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2)

# Get the active object
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply dimensions via scaling
cube.scale = (1.0, 0.5, 2.0)  # X=2, Y=1, Z=4
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (9.0, 8.0, -3.0)
cube.rotation_euler = (0.0, math.radians(35.0), 0.0)

# Add rigid body physics (Active)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0