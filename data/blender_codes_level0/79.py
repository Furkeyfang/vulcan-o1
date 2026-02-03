import bpy
import math

# Clear existing scene for clean execution
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,        # Default resolution for smooth appearance
    radius=2.2,
    depth=1.8,
    location=(-5.0, -3.0, 1.0)
)

# Get reference to the created cylinder
cylinder = bpy.context.active_object
cylinder.name = "Positioned_Cylinder"

# Apply 15° rotation around X-axis (convert to radians)
cylinder.rotation_euler.x = math.radians(15.0)

# Update object transformation
bpy.context.view_layer.update()

# Optional: Add a material for visual clarity
material = bpy.data.materials.new(name="Cylinder_Material")
material.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # Blue color
cylinder.data.materials.append(material)

print(f"Cylinder created at {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler.x):.1f}° on X-axis")