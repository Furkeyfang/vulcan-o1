import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.2,
    depth=3.2,
    location=(-4.0, -2.0, 1.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Apply 70° rotation around Z-axis (convert to radians)
cylinder.rotation_euler = (0.0, 0.0, math.radians(70.0))

# Ensure transformation is applied (optional for static mesh)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Set viewport display (optional)
cylinder.show_wire = True
cylinder.show_all_edges = True

# Set origin to geometry center (already true by default)
cylinder.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')