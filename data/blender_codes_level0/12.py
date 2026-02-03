import bpy
import math

# Clear existing mesh objects for clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    location=(-3.0, 2.0, 1.0)
)

# Get reference to created sphere
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply 180° rotation around Y-axis (π radians)
sphere.rotation_euler = (0.0, math.pi, 0.0)

# Optional: Apply transforms to make rotation permanent in mesh data
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Verify transforms
print(f"Sphere created: {sphere.name}")
print(f"Location: {sphere.location}")
print(f"Rotation: {sphere.rotation_euler}")
print(f"Radius: {sphere.dimensions.x / 2}")