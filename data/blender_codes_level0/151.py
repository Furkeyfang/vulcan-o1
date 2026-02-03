import bpy
import math

# Clear existing objects (optional, but ensures clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=5.0,
    location=(3.0, 0.0, 0.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Cylinder_Passive"

# Apply 15-degree rotation around Y-axis (convert to radians)
cylinder.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Add rigid body physics as passive
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'  # Use mesh for accurate collision
cylinder.rigid_body.collision_margin = 0.04   # Standard margin

# Ensure transformations are applied
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Optional: Visualize origin and axes for debugging
bpy.ops.object.empty_add(type='ARROWS', location=(3.0, 0.0, 0.0))
origin_marker = bpy.context.active_object
origin_marker.name = "Origin_Marker"
origin_marker.scale = (0.5, 0.5, 0.5)