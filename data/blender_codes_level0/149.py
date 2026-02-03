import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default 2×2×2 dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, -6.0))
cube = bpy.context.active_object
cube.name = "passive_cube"

# Scale to achieve 1×1×5 dimensions
# Default cube is 2 units wide, so scale factor = desired/2
cube.scale = (0.5, 0.5, 2.5)  # (1/2, 1/2, 5/2)

# Apply scale to make dimensions permanent in object data
bpy.ops.object.transform_apply(scale=True)

# Rotate 90° around Z-axis (convert degrees to radians)
cube.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Apply rotation to make it permanent
bpy.ops.object.transform_apply(rotation=True)

# Add rigid body physics with PASSIVE type
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Verify final properties
print(f"Cube created: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation: {cube.rotation_euler}")
print(f"Rigid Body Type: {cube.rigid_body.type}")