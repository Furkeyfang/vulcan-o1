import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with 32 segments and rings
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.0,  # Will scale to correct radius
    location=(0, 0, 0)  # Create at origin
)
sphere = bpy.context.active_object
sphere.name = "Sphere"

# Apply transformations based on parameters
sphere.scale = (1.1, 1.1, 1.1)  # Scale from unit radius to 1.1
sphere.location = (3.0, 7.0, -2.0)
sphere.rotation_euler = (0, 0, math.radians(60.0))  # Convert degrees to radians

# Apply transformations to make them base transformations
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Optional: Add material for visibility
mat = bpy.data.materials.new(name="Sphere_Material")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
if sphere.data.materials:
    sphere.data.materials[0] = mat
else:
    sphere.data.materials.append(mat)