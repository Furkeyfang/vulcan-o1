import bpy
import math

# Clear existing objects (optional, but ensures clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV Sphere with 32 segments and rings (default)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Passive_Sphere"

# Scale to achieve radius of 2.0
sphere.scale = (2.0, 2.0, 2.0)

# Apply scale to make radius intrinsic
bpy.ops.object.transform_apply(scale=True)

# Set location
sphere.location = (5.0, 0.0, 1.0)

# Rotate 45 degrees around Y-axis
sphere.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Add rigid body physics and set to PASSIVE
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'PASSIVE'

# Optionally, set mass (but not required for passive)
# sphere.rigid_body.mass = 10.0

print(f"Created passive sphere: {sphere.name}")
print(f"  Location: {sphere.location}")
print(f"  Rotation Y: {math.degrees(sphere.rotation_euler.y):.1f}°")
print(f"  Scale (applied): {sphere.scale}")