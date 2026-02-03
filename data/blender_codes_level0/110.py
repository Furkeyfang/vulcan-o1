import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube primitive (default 2x2x2 at origin)
bpy.ops.mesh.primitive_cube_add(size=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scale to achieve 4x1x1 dimensions (scale factors = desired/current = (4/2, 1/2, 1/2))
cube.scale = (2.0, 0.5, 0.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set position and rotation
cube.location = (3.0, 6.0, -1.0)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Verify dimensions
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation: {cube.rotation_euler}")