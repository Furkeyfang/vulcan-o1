import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified parameters
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.2,
    location=(8.0, 1.0, -1.0),
    rotation=(0.0, math.radians(90.0), 0.0)
)

# Rename the sphere object
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Optionally set smooth shading for better visualization
bpy.ops.object.shade_smooth()