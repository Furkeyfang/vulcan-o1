import bpy
import math

# Clear existing mesh objects (optional, for clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a default cylinder (32 vertices, radius=1, depth=2, aligned on Z)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=2.0,
    location=(0, 0, 0),
    rotation=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Apply scaling to achieve target radius and height
cylinder.scale = (1.5, 1.5, 1.0)  # Scale X/Y for radius, Z for height (2.0/2.0=1.0)

# Set rotation (around global Z-axis)
cylinder.rotation_euler = (0, 0, math.radians(10.0))

# Set final location
cylinder.location = (2.0, -3.0, -2.0)

# Apply transformations to make them intrinsic (freeze transform)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print("Cylinder created with:")
print(f"  Radius: {cylinder.dimensions.x / 2:.3f}")
print(f"  Height: {cylinder.dimensions.z:.3f}")
print(f"  Location: {cylinder.location}")
print(f"  Rotation (Z): {math.degrees(cylinder.rotation_euler.z):.1f}°")