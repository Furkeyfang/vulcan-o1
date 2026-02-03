import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.6,
    location=(6.0, 10.0, 3.0),
    segments=32,
    ring_count=16
)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 90-degree rotation around Z-axis (convert to radians)
sphere.rotation_euler = (0, 0, math.radians(90.0))

# Add rigid body physics with ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'MESH'
sphere.rigid_body.mass = 1.0  # Default mass

# Ensure transformation is applied
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print(f"Created active sphere at {sphere.location} with rotation {sphere.rotation_euler}")