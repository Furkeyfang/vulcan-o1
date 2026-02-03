import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with specified radius
# Default segments/rings are fine for demonstration
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.5, location=(0.0, 6.0, 0.0))
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply 15-degree rotation around X-axis (converted to radians)
sphere.rotation_euler = (math.radians(15.0), 0.0, 0.0)

# Optional: Set smooth shading for better visualization
bpy.ops.object.shade_smooth()

print(f"Sphere created: radius={sphere.dimensions.x/2}")
print(f"Location: {sphere.location}")
print(f"Rotation (radians): {sphere.rotation_euler}")