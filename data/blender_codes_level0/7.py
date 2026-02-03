import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default sphere (radius 1 at origin)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,
    location=(0, 0, 0),
    segments=32,
    ring_count=16
)

# Get reference to created sphere
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply transformations in correct order
# 1. Scale for radius (2x in all dimensions)
sphere.scale = (2.0, 2.0, 2.0)

# 2. Apply scale transformation
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 3. Set location
sphere.location = (6.0, 0.0, 1.0)

# 4. Apply rotation (45° around Y-axis)
sphere.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Apply rotation transformation
bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)

# Verify transformations
print(f"Sphere created with:")
print(f"  Name: {sphere.name}")
print(f"  Location: {sphere.location}")
print(f"  Rotation (Euler): {sphere.rotation_euler}")
print(f"  Scale: {sphere.scale}")
print(f"  Dimensions: {sphere.dimensions}")