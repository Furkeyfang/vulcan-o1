import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with radius 1.6
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.6, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "TargetSphere"

# Set location and rotation
sphere.location = (2.0, 4.0, 6.0)
sphere.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Verify transformation
print(f"Sphere created: {sphere.name}")
print(f"Location: {sphere.location}")
print(f"Rotation (radians): {sphere.rotation_euler}")
print(f"Rotation (degrees): ({math.degrees(sphere.rotation_euler.x)}, "
      f"{math.degrees(sphere.rotation_euler.y)}, "
      f"{math.degrees(sphere.rotation_euler.z)})")