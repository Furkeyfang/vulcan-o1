import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(7.0, 6.0, 2.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 60-degree rotation around Y-axis
sphere.rotation_euler = (0.0, math.radians(60.0), 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
# Optional: Set mass (default is 1.0 kg)
sphere.rigid_body.mass = 1.0