import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set transform
sphere.location = (6.0, 11.0, 6.0)
sphere.rotation_euler = (0, 0, math.pi/2)  # 90° Z rotation

# Add active rigid body
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'

# Optional: Set mass proportional to volume (density ~1)
sphere.rigid_body.mass = (4/3) * math.pi * (1.2**3)  # ~7.24 kg if unit=1m