import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube primitive (default 2m³)
bpy.ops.mesh.primitive_cube_add(size=2.0)

# Get reference to the cube
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Set dimensions to 2×2×4 by scaling (scale = desired_size / default_size)
# Default cube is 2×2×2, so scale Z by 2 to get 4m height
cube.scale = (1.0, 1.0, 2.0)

# Apply scale to make dimensions permanent in mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (-2.0, 8.0, -6.0)

# Set rotation (convert 30° to radians)
cube.rotation_euler = (0.0, 0.0, math.radians(30.0))

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0  # Default mass (adjustable)
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.1

# Optional: Set collision shape to BOX (optimal for cubes)
cube.rigid_body.collision_shape = 'BOX'

print(f"Created active cube at {cube.location} with rotation {cube.rotation_euler}")