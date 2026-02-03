import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with given dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=4.0,
    location=(-6.0, 0.0, 0.0)
)
cylinder = bpy.context.active_object
cylinder.name = "target_cylinder"

# Apply rotation: 30 degrees about X-axis
cylinder.rotation_euler = (math.radians(30.0), 0.0, 0.0)