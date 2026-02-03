import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2 in object space)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply dimensions via scale (4x2x1 in world space)
cube.scale = (2.0, 1.0, 0.5)  # From parameter_summary

# Set location and rotation
cube.location = (5.0, 6.0, -1.0)
cube.rotation_euler = (0.436332, 0.0, 0.0)  # 25° on X-axis

# Apply transformations (finalize scale/rotation)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Add Active Rigid Body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Optional: Set mass proportional to volume (4*2*1 = 8 m³). Density ~1 kg/m³.
cube.rigid_body.mass = 8.0