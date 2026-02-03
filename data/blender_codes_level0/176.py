import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default dimensions (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Scale to achieve 3×4×1 dimensions
# Default cube is 2×2×2, so scale factors: (3/2, 4/2, 1/2)
cube.scale = (1.5, 2.0, 0.5)

# Apply scale to make dimensions intrinsic
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (0.0, 9.0, 1.0)

# Apply X-axis rotation (20° converted to radians)
cube.rotation_euler = (math.radians(20.0), 0.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Optional: Set mass based on volume (assuming density 1 kg/m³)
# Volume = 3 × 4 × 1 = 12 m³
cube.rigid_body.mass = 12.0

print(f"Created active cube: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation (degrees): ({math.degrees(cube.rotation_euler.x):.1f}, 0, 0)")