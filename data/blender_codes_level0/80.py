import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "custom_cube"

# Apply scaling to achieve 4x2x2 dimensions
cube.scale = (2.0, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (1.0, 6.0, -1.0)
cube.rotation_euler = (0, math.radians(75.0), 0)

# Optional: Set visual properties
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)
cube.data.materials.append(mat)

print(f"Created cube '{cube.name}' at {cube.location} with rotation {cube.rotation_euler}")