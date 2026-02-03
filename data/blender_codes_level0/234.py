import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location and rotation
sphere.location = (-1.0, 7.0, 11.0)
sphere.rotation_euler = (0.0, math.radians(90.0), 0.0)  # 90° around Y

# Add rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
# Keep default mass (calculated from volume and density) and other physics properties