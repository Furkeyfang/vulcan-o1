import bpy
import math

# Clear existing mesh objects for clean execution
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.1, location=(0, -9, 0))
sphere = bpy.context.active_object
sphere.name = "Sphere"

# Apply 90° rotation around Z-axis
sphere.rotation_euler = (0, 0, math.radians(90))

# Verify transformations
print(f"Sphere created: {sphere.name}")
print(f"Location: {sphere.location}")
print(f"Rotation (degrees): {tuple(math.degrees(r) for r in sphere.rotation_euler)}")