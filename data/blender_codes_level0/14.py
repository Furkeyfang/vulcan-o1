import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default 2x2x2 dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "PositionedCube"

# Set dimensions to 3×3×1 by scaling
cube.dimensions = (3.0, 3.0, 1.0)

# Apply scale to make dimensions permanent
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (2.0, -2.0, 0.0)
cube.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Optional: Add passive rigid body for physics simulation
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

print(f"Cube created at {cube.location} with rotation {cube.rotation_euler}")