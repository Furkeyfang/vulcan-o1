import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5)
sphere = bpy.context.active_object
sphere.name = "ActiveSphere"

# Set location
sphere.location = (1.0, 6.0, 3.0)

# Set rotation (60° around X-axis, converted to radians)
sphere.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Add active rigid body component
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'

# Optional: Set mass if different from default (1.0kg)
# sphere.rigid_body.mass = 2.0

print(f"Created active sphere at {sphere.location} with rotation {sphere.rotation_euler}")