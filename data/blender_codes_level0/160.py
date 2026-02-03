import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply non-uniform scaling for 3x2x4 dimensions
cube.scale = (1.5, 1.0, 2.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-1.0, 7.0, -7.0)
cube.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
# Optional: Set mass based on volume (assuming density 1 kg/m³)
cube.rigid_body.mass = 24.0  # Volume = 3×2×4 = 24 m³