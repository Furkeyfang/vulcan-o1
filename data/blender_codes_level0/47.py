import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=2.0,
    depth=3.0,
    location=(-7.0, 0.0, 3.5)  # Center at Z=3.5 for base at Z=2
)
cylinder = bpy.context.active_object
cylinder.name = "TargetCylinder"

# Apply 25° rotation around X-axis (converted to radians)
cylinder.rotation_euler[0] = math.radians(25.0)

# Update scene
bpy.context.view_layer.update()

# Optional: Add a ground plane for visual reference
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"