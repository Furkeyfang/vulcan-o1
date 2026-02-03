import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default 2x2x2 dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "cube_active"

# Scale to achieve 2x5x2 dimensions
# Default cube is 2x2x2, so scale factors: (2/2, 5/2, 2/2) = (1.0, 2.5, 1.0)
cube.scale = (1.0, 2.5, 1.0)

# Apply scale transformation for accurate physics
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (-4.0, 7.0, 5.0)

# Set rotation (30 degrees around X-axis)
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Optionally set mass (1kg per cubic meter * volume = 1*20 = 20kg)
cube.rigid_body.mass = 20.0

print(f"Created active cube at {cube.location} with rotation {cube.rotation_euler}")