import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with specified radius
# The 'add_uv_sphere' operator uses diameter, so we set radius after creation
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0)
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Set radius to 3.0 (scale the mesh data, not the object scale)
sphere.data.transform(mathutils.Matrix.Scale(3.0, 4))
sphere.data.update()

# Set location
sphere.location = (10.0, 0.0, 0.0)

# Apply rotation about Z-axis (45 degrees converted to radians)
sphere.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Apply transforms to make transformations explicit
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Optional: Add a simple material for visibility
mat = bpy.data.materials.new(name="Sphere_Material")
mat.use_nodes = True
sphere.data.materials.append(mat)

print(f"Sphere created:")
print(f"  Radius: {sphere.dimensions.x/2:.3f}")
print(f"  Location: {sphere.location}")
print(f"  Rotation: {math.degrees(sphere.rotation_euler.z):.1f}° about Z-axis")