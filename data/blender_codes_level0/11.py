import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with specified dimensions
# Default Blender cube is 2x2x2, so we scale by half dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply dimensions (scale from default 2m cube)
cube.scale = (0.5, 1.0, 1.0)  # Converts 2x2x2 to 1x2x2
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (0.0, 5.0, 0.0)
cube.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Apply all transformations
bpy.ops.object.transform_apply(location=True, rotation=True)

# Optional: Add wireframe display for clarity
cube.display_type = 'WIRE'
cube.show_wire = True
cube.show_all_edges = True

print(f"Cube created at {cube.location}")
print(f"Final dimensions: {cube.dimensions}")
print(f"Rotation: {cube.rotation_euler}")