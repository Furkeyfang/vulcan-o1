import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified parameters
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.1,
    location=(0.0, 10.0, 0.0),
    segments=32,
    ring_count=16
)

# Get reference to the created sphere
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 90° rotation around Z-axis (convert degrees to radians)
sphere.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Add rigid body physics with ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # Default mass
sphere.rigid_body.friction = 0.5  # Default friction
sphere.rigid_body.restitution = 0.5  # Default bounciness

# Optional: Set collision shape to SPHERE for optimal performance
sphere.rigid_body.collision_shape = 'SPHERE'

print(f"Created active sphere: {sphere.name}")
print(f"  Radius: {sphere.dimensions.x / 2}")
print(f"  Location: {sphere.location}")
print(f"  Rotation: {math.degrees(sphere.rotation_euler.z)}° around Z-axis")