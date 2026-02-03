import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.7,
    depth=3.3,
    location=(2.0, 2.0, -6.0)
)
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply rotation (25° around Y-axis)
cylinder.rotation_euler = (0.0, math.radians(25.0), 0.0)

# Optional: Set object origin to base for clarity (height starts at z=-6)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
cylinder.location.z += 1.65  # Half height adjustment