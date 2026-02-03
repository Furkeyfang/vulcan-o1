import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply scaling to achieve 4x2x1 dimensions (scale default 2m cube by (2,1,0.5))
cube.scale = (2.0, 1.0, 0.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (5.0, -1.0, -1.0)
cube.rotation_euler = (math.radians(25.0), 0.0, 0.0)

# Optional: Add a material for visibility
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

print(f"Cube '{cube.name}' created at {cube.location} with dimensions {cube.dimensions}")