import bpy
import math

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(-4, 5, 4))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 90-degree rotation about the Z-axis (convert to radians)
sphere.rotation_euler = (0, 0, math.radians(90))

# Add rigid body physics and set to ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'

# Optionally, set mass (default is 1.0 kg) and other physics properties
# sphere.rigid_body.mass = 1.0