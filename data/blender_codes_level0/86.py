import bpy
from math import radians

# Clear existing mesh objects (optional, to start fresh)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with radius 0.7
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(-6.0, 4.0, 3.0))
sphere = bpy.context.active_object
sphere.name = "Sphere"

# Apply 15-degree rotation around Y-axis
sphere.rotation_euler = (0, radians(15.0), 0)

# (Optional) Set smooth shading for better appearance
bpy.ops.object.shade_smooth()