import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.6,
    depth=2.9,
    location=(-3.0, 5.0, -4.0),
    rotation=(0.261799, 0.0, 0.0)  # 15° in radians around X
)

cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Verify transformations
print(f"Cylinder created: {cylinder.name}")
print(f"Location: {cylinder.location}")
print(f"Rotation (rad): {cylinder.rotation_euler}")
print(f"Dimensions: Radius=1.6, Height=2.9")