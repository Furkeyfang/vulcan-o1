import bpy
import math

# Clear existing mesh objects (optional clean start)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.4,
    depth=4.1,
    location=(0.0, 1.0, 9.0),
    rotation=(0.0, math.radians(60.0), 0.0)
)

# Rename the cylinder object
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Optional: Set smooth shading for better visual appearance
bpy.ops.object.shade_smooth()

# Optional: Add a material for visual distinction
mat = bpy.data.materials.new(name="Cylinder_Material")
mat.use_nodes = True
cylinder.data.materials.append(mat)