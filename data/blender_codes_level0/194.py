import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.4, location=(2.0, 8.0, 8.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 60-degree rotation around X-axis (convert to radians)
sphere.rotation_euler[0] = math.radians(60.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
# Optional: Explicitly set mass (default is 1.0 kg)
sphere.rigid_body.mass = 1.0

# Ensure the transformation is applied (location and rotation are set, scale is 1)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)