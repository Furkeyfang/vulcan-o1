import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with radius 1
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,
    location=(0, 0, 0)  # Will set location separately
)
sphere = bpy.context.active_object
sphere.name = "Sphere_Object"

# Set location
sphere.location = (5.0, 5.0, 5.0)

# Set rotation (120 degrees about Z-axis)
sphere.rotation_euler = (0.0, 0.0, math.radians(120.0))

# Optional: Set display properties
sphere.display_type = 'SOLID'
bpy.context.object.data.use_auto_smooth = True

# Verify transformations
print(f"Sphere created: {sphere.name}")
print(f"Location: {sphere.location}")
print(f"Rotation (radians): {sphere.rotation_euler}")
print(f"Radius: {sphere.dimensions.x / 2}")  # Approximate verification