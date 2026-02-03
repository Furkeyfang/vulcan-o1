import bpy
import math

# Clear existing objects (optional, to start fresh)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV sphere with 32 segments and 16 rings (defaults)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.0,  # Will be scaled immediately
    location=(0, 0, 0)
)
sphere = bpy.context.active_object
sphere.name = "Sphere"

# Set the radius by scaling uniformly (since default radius is 1, scale by 2)
sphere.scale = (2.0, 2.0, 2.0)

# Apply the scale to make the radius intrinsic
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set the location
sphere.location = (0.0, 0.0, 8.0)

# Set the rotation: 90 degrees around X-axis
sphere.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Optional: Set object origin to geometry center (already at center by default)
# bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')