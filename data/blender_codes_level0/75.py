import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.1,
    depth=2.2,
    location=(7.0, -1.0, -2.0),
    rotation=(0, 0, math.radians(45.0))
)
cylinder = bpy.context.active_object
cylinder.name = "cylinder_001"