import bpy
import math

# Clear existing objects (optional but recommended for clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.9,
    location=(0.0, 11.0, -6.0)
)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 30° rotation around X-axis (convert to radians)
sphere.rotation_euler[0] = math.radians(30.0)

# Add rigid body physics as ACTIVE
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # Default mass
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Update viewport to show changes
bpy.context.view_layer.update()

print(f"Created active sphere:")
print(f"  Radius: {sphere.dimensions[0]/2}")
print(f"  Location: {sphere.location}")
print(f"  Rotation (X): {math.degrees(sphere.rotation_euler[0])}°")
print(f"  Rigid Body Type: {sphere.rigid_body.type}")