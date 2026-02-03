import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=3.0,
    location=(2.0, 0.0, 2.0)
)

# Get reference to the created cylinder
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply rotation (60 degrees around X-axis)
cylinder.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Optional: Set material for visualization
material = bpy.data.materials.new(name="CylinderMaterial")
material.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
cylinder.data.materials.append(material)

# Add reference grid for spatial context
bpy.ops.mesh.primitive_grid_add(
    x_subdivisions=10,
    y_subdivisions=10,
    size=10.0,
    location=(0, 0, 0)
)
grid = bpy.context.active_object
grid.name = "ReferenceGrid"