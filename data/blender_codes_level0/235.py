import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
# Default Blender cylinder: radius=1, depth=2, aligned with Z-axis
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=2.3,
    depth=2.2,
    location=(2.0, 0.0, -11.0),
    rotation=(0.2617993877991494, 0.0, 0.0)  # 15° around X-axis
)

cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Add rigid body physics as passive/static object
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'

# Optional: Set display properties for clarity
cylinder.display_type = 'SOLID'
cylinder.show_wire = True