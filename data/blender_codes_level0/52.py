import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create base cube (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling for 2x2x4 dimensions
cube.scale = (1.0, 1.0, 2.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-2.0, 0.0, -6.0)
cube.rotation_euler = (0.0, 0.0, math.radians(30.0))

# Optional: Add visual material for clarity
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

# Update viewport
bpy.context.view_layer.update()