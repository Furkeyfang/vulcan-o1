import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with unit dimensions initially
bpy.ops.mesh.primitive_cube_add(size=1.0)

# Get reference to the cube
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply dimensions (scale) to achieve 2x2x3
cube.dimensions = (2.0, 2.0, 3.0)

# Set location and rotation
cube.location = (3.0, 7.0, 3.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Apply scale to make dimensions permanent
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Optional: Set mass based on volume (assuming density 1 kg/m³)
# Volume = 2*2*3 = 12 cubic units
cube.rigid_body.mass = 12.0

print(f"Created active cube at {cube.location} with rotation {cube.rotation_euler}")