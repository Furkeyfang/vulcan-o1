import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.3,
    location=(-7.0, 6.0, -2.0),
    scale=(1, 1, 1)
)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 45° rotation around X-axis (convert to radians)
rotation_rad = math.radians(45.0)
sphere.rotation_euler = (rotation_rad, 0.0, 0.0)

# Add rigid body physics with ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'

# Set reasonable default physics properties
sphere.rigid_body.mass = 1.0
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Apply rotation transformation to mesh data
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

print(f"Created active sphere at {sphere.location}")
print(f"Rotation: {math.degrees(sphere.rotation_euler.x):.1f}° around X-axis")