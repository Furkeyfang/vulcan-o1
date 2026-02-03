import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV Sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.5)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location and rotation (converting degrees to radians)
sphere.location = (0.0, 10.0, 0.0)
sphere.rotation_euler = (math.radians(15.0), 0.0, 0.0)

# Add Active Rigid Body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'