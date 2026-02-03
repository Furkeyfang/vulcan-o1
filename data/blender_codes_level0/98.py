import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5)
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply location transform
sphere.location = (7.0, -3.0, 3.0)

# Apply rotation (convert degrees to radians)
sphere.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Update scene
bpy.context.view_layer.update()

print(f"Created sphere '{sphere.name}'")
print(f"  Location: {sphere.location}")
print(f"  Rotation: {math.degrees(sphere.rotation_euler.y):.1f}° around Y-axis")
print(f"  Radius: {sphere.dimensions.x/2:.3f} (verified)")