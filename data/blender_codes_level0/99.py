import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
# Default cylinder in Blender is aligned with Z-axis, centered at origin
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=6.0,
    location=(-1.0, -1.0, 10.0)
)

cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply 30-degree rotation around Z-axis
cylinder.rotation_euler = (0, 0, math.radians(30.0))

# Optional: Set object origin to geometry center (already centered by default)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

print(f"Cylinder created at {cylinder.location} with rotation {cylinder.rotation_euler}")