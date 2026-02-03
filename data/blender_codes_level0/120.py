import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with specified dimensions
# Note: bpy.ops.mesh.primitive_cube_add creates a 2x2x2 cube by default, so we scale
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply dimensions (scale)
cube.scale = (2.5, 0.5, 0.5)  # Default 1m cube becomes 5x1x1 after scaling
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (6.0, 7.0, 0.0)
cube.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Assign active rigid body properties
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
# Optional: Set mass based on volume (5 m³) and density (1 kg/m³ default)
cube.rigid_body.mass = 5.0