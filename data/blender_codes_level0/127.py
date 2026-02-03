import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Scale to desired dimensions (3×1×2)
# Default cube is 2m, so scale factors = desired/2
cube.scale = (1.5, 0.5, 1.0)  # (3/2, 1/2, 2/2)

# Apply scale to avoid shearing
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-3.0, 0.0, 5.0)
cube.rotation_euler = (math.radians(10.0), 0.0, 0.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set collision margin for stability
cube.rigid_body.collision_margin = 0.0