import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.3, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply X-axis rotation (60 degrees)
sphere.rotation_euler.x = math.radians(60.0)

# Set location after rotation to maintain correct orientation
sphere.location = (-12.0, 10.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'