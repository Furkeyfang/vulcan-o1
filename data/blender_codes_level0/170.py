import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.4,
    location=(-8.0, 6.0, 0.0),
    segments=32,
    ring_count=32
)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 15° rotation around X-axis (convert to radians)
sphere.rotation_euler = (math.radians(15.0), 0.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Optional: Enable gravity in scene (default is already -9.81 Z)
bpy.context.scene.use_gravity = True

print(f"Created sphere: {sphere.name}")
print(f"Radius: {sphere.dimensions.x/2}")
print(f"Location: {sphere.location}")
print(f"Rotation: {sphere.rotation_euler}")