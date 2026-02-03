import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube primitive (default size 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to achieve dimensions 4x3x1
cube.scale = (2.0, 1.5, 0.5)

# Apply scale to avoid distortion in transformations
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-4.0, 3.0, 4.0)
# Convert degrees to radians
cube.rotation_euler = (0.0, math.radians(35.0), 0.0)

# Optional: Add rigid body if simulation is desired (passive by default)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set display to wireframe or solid, and set origin to geometry
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

print("Cube created successfully.")