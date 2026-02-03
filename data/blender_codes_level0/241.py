import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Scale to achieve 1x1x6 dimensions (since default cube is 2 units per side)
# scale_factor = desired_length / default_length (2.0)
scale_x = 1.0 / 2.0
scale_y = 1.0 / 2.0
scale_z = 6.0 / 2.0
cube.scale = (scale_x, scale_y, scale_z)

# Apply scale to avoid distortion in physics
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (12.0, 0.0, 0.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Add rigid body physics as passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set display to see dimensions clearly
bpy.context.object.display_type = 'WIRE'