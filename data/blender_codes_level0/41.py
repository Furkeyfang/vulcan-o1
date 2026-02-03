import bpy
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default dimensions (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0,0,0))
cube = bpy.context.active_object
cube.name = "TaskCube"

# Apply non-uniform scaling to achieve 1x2x3 dimensions
# Since default cube is 2m³, scale factors: (1/2, 3/2, 2/2) = (0.5, 1.5, 1.0)
cube.scale = (0.5, 1.5, 1.0)

# Apply scale to make dimensions permanent in mesh data
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set final transform: location and rotation
cube.location = (-6.0, 1.0, 1.0)
cube.rotation_euler = (0.0, radians(45.0), 0.0)

# Apply rotation to mesh data (optional, keeps transform clean)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Verify dimensions
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation: {cube.rotation_euler}")