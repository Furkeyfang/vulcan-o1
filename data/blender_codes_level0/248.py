import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default dimensions (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Scale to achieve 3x1x5 dimensions
# Since default cube is 2x2x2, scale factors = desired/2
cube.scale = (1.5, 0.5, 2.5)  # (3/2, 1/2, 5/2)

# Apply scale to make transformations clean
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (0.0, 9.0, 12.0)
cube.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Add rigid body physics (Active)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Optionally add a ground plane for the cube to fall onto
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set gravity to default -Z (if not already)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

print(f"Created active cube: {cube.name}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation Y: {math.degrees(cube.rotation_euler.y):.1f}°")