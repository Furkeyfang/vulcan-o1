import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,
    location=(-2.0, -2.0, -2.0),
    scale=(1.0, 1.0, 1.0)
)

# Get reference to the created sphere
sphere = bpy.context.active_object
sphere.name = "Rotated_Sphere"

# Apply 120° rotation around Z-axis (convert degrees to radians)
rotation_angle = math.radians(120.0)
sphere.rotation_euler = (0.0, 0.0, rotation_angle)

# Update scene
bpy.context.view_layer.update()

print(f"Created sphere '{sphere.name}'")
print(f"  Radius: {sphere.dimensions.x/2:.3f}")
print(f"  Location: {sphere.location}")
print(f"  Rotation (Z-axis): {math.degrees(sphere.rotation_euler.z):.1f}°")