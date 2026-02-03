import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius at origin
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply transformations
sphere.location = (-3.0, 1.0, 7.0)
sphere.rotation_euler = (0.0, math.radians(60.0), 0.0)

# Update scene
bpy.context.view_layer.update()

print(f"Created sphere '{sphere.name}'")
print(f"  Radius: {sphere.dimensions.x/2}")
print(f"  Location: {sphere.location}")
print(f"  Rotation (degrees): {tuple(math.degrees(r) for r in sphere.rotation_euler)}")