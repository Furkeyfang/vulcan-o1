import bpy
import math

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube with dimensions 2x2x1
# Default Blender cube is 2x2x2, so we scale by (1, 1, 0.5) to get 2x2x1
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply dimensions: scale in Z by 0.5 to get height 1 (since base size is 2)
cube.scale = (1.0, 1.0, 0.5)

# Apply the scale transformation to make it the actual mesh data
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location
cube.location = (-1.0, 4.0, -1.0)

# Set rotation: 25 degrees around X-axis, converted to radians
cube.rotation_euler = (math.radians(25.0), 0.0, 0.0)