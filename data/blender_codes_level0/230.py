import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.9,
    location=(-8.0, 10.0, 0.0),
    scale=(1.0, 1.0, 1.0)
)
sphere = bpy.context.active_object
sphere.name = "sphere_active"

# Apply 20° rotation about Z-axis
sphere.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'
sphere.rigid_body.mass = 1.0  # Will be overridden by mesh volume
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.3

# Optional: Ensure proper scale (already unit scale)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

print(f"Created active sphere '{sphere.name}'")
print(f"  Radius: {sphere.dimensions.x/2:.3f} m")
print(f"  Location: {sphere.location}")
print(f"  Rotation: {math.degrees(sphere.rotation_euler.z):.1f}° about Z")