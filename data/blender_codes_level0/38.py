import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with 32 segments and rings for smooth appearance
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.2,
    location=(7.0, 0.0, 2.0)
)
sphere = bpy.context.active_object
sphere.name = "Sphere_Object"

# Apply 60-degree rotation around Y-axis (converted to radians)
sphere.rotation_euler = (0.0, math.radians(60.0), 0.0)

# Optional: Add a material for visibility
material = bpy.data.materials.new(name="Sphere_Material")
material.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
sphere.data.materials.append(material)