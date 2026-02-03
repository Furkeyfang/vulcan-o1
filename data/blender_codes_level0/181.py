import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add default cube (2x2x2 units)
bpy.ops.mesh.primitive_cube_add(size=2.0)

# Get reference to cube
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Set scale to achieve 2x1x5 dimensions
cube.scale = (1.0, 0.5, 2.5)

# Apply scale to make dimensions actual mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (-2.0, 0.0, -2.0)

# Set rotation (45° around Z-axis)
cube.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Apply rotation to mesh data
bpy.ops.object.transform_apply(rotation=True)

# Add rigid body physics (passive/static)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Verify final dimensions
print(f"Cube created at {cube.location}")
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube rotation: {cube.rotation_euler}")