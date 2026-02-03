import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a default cube (1x1x1)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to 1x1x2 dimensions (scale Z by 2)
cube.scale = (1.0, 1.0, 2.0)
bpy.context.view_layer.update()

# Apply rotation: 180 degrees around Y-axis
cube.rotation_euler = (0.0, math.radians(180.0), 0.0)
bpy.context.view_layer.update()

# Move to final position (1, 1, 6)
cube.location = (1.0, 1.0, 6.0)

# Apply transforms to make scale and rotation explicit in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print(f"Cube '{cube.name}' created with dimensions {cube.dimensions}")
print(f"Location: {cube.location}, Rotation: {cube.rotation_euler}")