import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default dimensions (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Placed_Cube"

# Apply dimensions: scale from default 2m cube to desired 2×4×1
# Scale factors = desired / default
scale_x = 2.0 / 2.0  # 1.0
scale_y = 4.0 / 2.0  # 2.0
scale_z = 1.0 / 2.0  # 0.5
cube.scale = (scale_x, scale_y, scale_z)

# Apply scale transformation to mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (0.0, -6.0, 2.0)

# Set rotation: 90° around X-axis
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Optional: Add passive rigid body for potential physics (commented out)
# bpy.ops.rigidbody.object_add()
# cube.rigid_body.type = 'PASSIVE'

print(f"Created {cube.name} at {cube.location} with rotation {cube.rotation_euler}")