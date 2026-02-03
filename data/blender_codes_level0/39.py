import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,
    depth=4.0,
    location=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply rotation (30 degrees about X-axis)
cylinder.rotation_euler[0] = math.radians(30)

# Apply translation
cylinder.location = (-1.0, 5.0, -1.0)

# Optional: Set smooth shading and single vertex color for clarity
bpy.ops.object.shade_smooth()
cylinder.data.materials.clear()
mat = bpy.data.materials.new(name="CylinderMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Reddish color
cylinder.data.materials.append(mat)

print(f"Cylinder created at {cylinder.location} with rotation {cylinder.rotation_euler}")