import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube primitive (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube_2x4x1"

# Apply scaling to achieve 2x4x1 dimensions
# Default cube vertices range from -1 to +1 in all axes (2m side length)
# Scale factors: (2/2=1.0, 4/2=2.0, 1/2=0.5)
cube.scale = (1.0, 2.0, 0.5)
bpy.ops.object.transform_apply(scale=True)

# Apply rotation (90° around X-axis)
cube.rotation_euler[0] = math.radians(90.0)
bpy.ops.object.transform_apply(rotation=True)

# Set final location
cube.location = (0.0, 8.0, 2.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'CONVEX_HULL'
cube.rigid_body.mass = 10.0  # Reasonable default mass (2*4*1=8m³ * density)

# Optional: Add a ground plane for stability demonstration
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set viewport display for clarity
cube.show_bounds = True
cube.display_type = 'SOLID'