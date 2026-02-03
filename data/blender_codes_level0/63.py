import bpy
import math

# Clear existing objects (optional, for clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=1.5,
    location=(-2.0, 6.0, 1.0)
)

cylinder = bpy.context.active_object
cylinder.name = "cylinder_001"

# Apply 45-degree rotation around Z-axis (convert degrees to radians)
cylinder.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Optional: Apply transforms to make rotation permanent in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print(f"Cylinder '{cylinder.name}' created at {cylinder.location} with rotation {cylinder.rotation_euler}")