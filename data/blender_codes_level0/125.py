import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with radius 1 at origin
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Passive_Sphere"

# Apply transformations from parameter summary
sphere.location = (-2.0, 0.0, -2.0)
sphere.rotation_euler = (0.0, 0.0, 120.0 * math.pi / 180.0)  # 120° Z-rotation

# Add passive rigid body
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'PASSIVE'

# Set collision shape to sphere (optimal for performance)
sphere.rigid_body.collision_shape = 'SPHERE'