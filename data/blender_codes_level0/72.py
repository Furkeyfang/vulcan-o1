import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default dimensions (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, enter_editmode=False, align='WORLD')

cube = bpy.context.active_object
cube.name = "RectangularPrism"

# Apply scaling to achieve 5x1x2 dimensions
cube.scale.x = 5.0 / 2.0  # Original cube is 2 units wide
cube.scale.y = 1.0 / 2.0
cube.scale.z = 2.0 / 2.0

# Apply scale transformation to make scaling permanent
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location.x = -1.0
cube.location.y = 5.0
cube.location.z = 3.0

# Apply 90° rotation around Z-axis
cube.rotation_euler.z = math.radians(90.0)

# Update scene
bpy.context.view_layer.update()

print(f"Created {cube.name} at {cube.location} with rotation {cube.rotation_euler}")