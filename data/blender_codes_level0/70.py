import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create UV sphere with 32 segments and rings for smooth appearance
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.4,
    location=(-8.0, 0.0, 0.0),
    segments=32,
    ring_count=16
)
sphere = bpy.context.active_object
sphere.name = "Positioned_Sphere"

# Apply 15-degree rotation around X-axis (convert to radians)
sphere.rotation_euler.x = math.radians(15.0)

# Update viewport and set smooth shading
bpy.context.view_layer.update()
bpy.ops.object.shade_smooth()

# Optional: Add a material for visual clarity
mat = bpy.data.materials.new(name="Sphere_Material")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # RGBA
sphere.data.materials.append(mat)

print(f"Sphere created at {sphere.location} with radius 2.4, rotated {sphere.rotation_euler.x:.4f} rad around X.")