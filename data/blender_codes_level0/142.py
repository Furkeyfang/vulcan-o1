import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV sphere with radius 2
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=(0.0, 9.0, 8.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply rotation: 90 degrees about X-axis
sphere.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # Default mass

print(f"Created active sphere at {sphere.location} with radius 2.0")