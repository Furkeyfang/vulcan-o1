import bpy
import math
from mathutils import Euler

# Clear existing objects (optional, but ensures clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,  # Standard resolution
    radius=0.8,
    depth=3.0,
    location=(-3.0, 4.0, -2.0),
    rotation=Euler((0.0, 0.0, math.radians(120.0)), 'XYZ')
)

# Rename for clarity
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Optional: Apply rotation to object data for clean transforms
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Verify parameters
print(f"Cylinder created:")
print(f"  Radius: {cylinder.dimensions.x / 2:.3f}")
print(f"  Height: {cylinder.dimensions.z:.3f}")
print(f"  Location: {cylinder.location}")
print(f"  Rotation (Euler Z): {math.degrees(cylinder.rotation_euler.z):.1f}°")