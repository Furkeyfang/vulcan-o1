import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=2.0,
    location=(0, 0, 0)
)

cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply transformations
cylinder.location = (3.0, 3.0, -3.0)
cylinder.rotation_euler = (0, math.radians(45.0), 0)

# Verify dimensions (optional but good practice)
cylinder.data.name = "CylinderMesh"
print(f"Cylinder created at {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler.y):.1f}° around Y-axis")