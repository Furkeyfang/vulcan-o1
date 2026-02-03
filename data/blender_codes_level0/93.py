import bpy
import math
from mathutils import Euler

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling to achieve 5×1×3 dimensions
cube.scale = (2.5, 0.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-8.0, 1.0, 0.0)
cube.rotation_euler = Euler((0.0, 0.0, math.radians(30.0)), 'XYZ')

# Optional: Add material for visibility
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

print(f"Cube '{cube.name}' created at {cube.location} with rotation {cube.rotation_euler}")