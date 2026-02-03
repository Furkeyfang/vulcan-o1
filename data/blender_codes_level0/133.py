import bpy
import math

# Clear existing mesh objects (optional cleanup)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create base cube (default 1m³ at origin)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply dimensions: scale in Z direction for 2m height
cube.scale = (1.0, 1.0, 2.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (1.0, 0.0, 6.0)
cube.rotation_euler = (0.0, math.pi, 0.0)  # 180° around Y

# Add rigid body physics as PASSIVE
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set display properties for clarity
cube.display_type = 'SOLID'
bpy.context.space_data.shading.type = 'SOLID'