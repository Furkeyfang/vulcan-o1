import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.2)
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Set location
sphere.location = (9.0, 0.0, 1.0)

# Apply rotation (30° around X-axis)
sphere.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Optional: Set smooth shading for better visualization
bpy.ops.object.shade_smooth()

print(f"Created sphere '{sphere.name}'")
print(f"  Radius: {sphere.dimensions.x/2:.1f}")
print(f"  Location: {sphere.location}")
print(f"  Rotation: {[math.degrees(r) for r in sphere.rotation_euler]}")