import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.6,
    depth=2.4,
    location=(1.0, -7.0, 1.0)
)
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply 90° rotation around X-axis (π/2 radians)
cylinder.rotation_euler[0] = math.radians(90.0)

# Update transformation
bpy.context.view_layer.update()

# Optional: Add ground plane for reference
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"