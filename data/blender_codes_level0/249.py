import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2m³)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "passive_cube"

# Scale to desired dimensions (5×2×2)
cube.scale = (2.5, 1.0, 1.0)

# Apply scale transform to make it actual mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (9.0, 0.0, 5.0)
cube.rotation_euler = (0.0, 0.0, math.radians(30.0))

# Add rigid body physics (passive/static)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to match mesh exactly
cube.rigid_body.collision_shape = 'MESH'

# Verify transformations
print(f"Created: {cube.name}")
print(f"Dimensions: {cube.dimensions}")
print(f"Location: {cube.location}")
print(f"Rotation: {math.degrees(cube.rotation_euler.z):.1f}° Z")