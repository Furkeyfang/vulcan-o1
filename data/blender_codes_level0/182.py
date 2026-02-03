import bpy
import math

# Clear the scene of default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV Sphere with the specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.2)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location and rotation (converting degrees to radians)
sphere.location = (9.0, 8.0, 1.0)
sphere.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add rigid body physics and set to ACTIVE
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
# Set collision shape to SPHERE for accuracy (default is convex hull)
sphere.rigid_body.collision_shape = 'SPHERE'

# Optional: Set a mass proportional to volume (density of 1)
# Volume of sphere = (4/3)*pi*r^3
volume = (4/3) * math.pi * (3.2**3)
sphere.rigid_body.mass = volume

print(f"Created active sphere at {sphere.location} with radius 3.2 and X-rotation 30°.")