import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location and rotation
sphere.location = (-3.0, 6.0, 7.0)
sphere.rotation_euler = (0.0, math.radians(60.0), 0.0)  # Y-axis rotation

# Add active rigid body
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'

# Optional: Adjust rigid body settings for clarity
sphere.rigid_body.mass = 1.0
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.5

print(f"Created active sphere at {sphere.location} with rotation {sphere.rotation_euler}")