import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.5,
    location=(1.0, -3.0, 3.0),
    scale=(1, 1, 1)
)
sphere = bpy.context.active_object
sphere.name = "TargetSphere"

# Apply 60° rotation about X-axis (convert to radians)
sphere.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Update mesh transformations
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print(f"Sphere created: {sphere.name}")
print(f"Location: {sphere.location}")
print(f"Rotation (radians): {sphere.rotation_euler}")
print(f"Radius: {sphere.dimensions.x / 2}")