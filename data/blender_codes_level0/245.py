import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with proper dimensions
# Default cube is 2x2x2, scale to 2x2x3
bpy.ops.mesh.primitive_cube_add(size=1.0)  # Unit cube (2m when scaled)
cube = bpy.context.active_object
cube.name = "Passive_Cube_2x2x3"

# Set scale for dimensions (2,2,3)
# Scale factors: desired / default = (2/2, 2/2, 3/2) = (1, 1, 1.5)
cube.scale = (1.0, 1.0, 1.5)

# Apply scale to make dimensions actual
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (11.0, 0.0, -4.0)

# Set rotation (60 degrees around Y-axis)
cube.rotation_euler = (0.0, math.radians(60.0), 0.0)

# Add rigid body physics with PASSIVE type
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX for efficiency
cube.rigid_body.collision_shape = 'BOX'

print(f"Created passive cube at {cube.location}")
print(f"Dimensions: {cube.dimensions}")
print(f"Rotation Y: {math.degrees(cube.rotation_euler.y):.1f}°")