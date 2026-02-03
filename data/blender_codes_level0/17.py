import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=2.0,
    depth=1.0,
    location=(0.0, 0.0, -5.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Cylinder"

# Apply 45° rotation about Y-axis
cylinder.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Ensure transformation is applied (optional for static object)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

print(f"Created cylinder '{cylinder.name}' at {cylinder.location} with rotation {cylinder.rotation_euler}")