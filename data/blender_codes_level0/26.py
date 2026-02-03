import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.75,
    depth=2.5,
    location=(1.0, 2.0, -4.0)
)

# Get reference to the cylinder
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply rotation (40° about Y-axis)
cylinder.rotation_euler = (0.0, math.radians(40.0), 0.0)

# Optional: Add material for visibility
material = bpy.data.materials.new(name="CylinderMaterial")
material.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
cylinder.data.materials.append(material)

print(f"Cylinder created at location: {cylinder.location}")
print(f"Cylinder rotation (degrees): {math.degrees(cylinder.rotation_euler.y)}° about Y-axis")