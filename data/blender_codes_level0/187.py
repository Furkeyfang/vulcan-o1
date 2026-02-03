import bpy
import math

# Clear existing objects (optional, for clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified radius and height
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.9,
    depth=3.6,
    location=(3.0, 0.0, -8.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply 45-degree rotation around Z-axis (convert degrees to radians)
cylinder.rotation_euler = (0, 0, math.radians(45.0))

# Add rigid body physics and set to PASSIVE
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'  # Use mesh for accurate cylinder collision

# Optional: Set display to wireframe to see rotation effect
cylinder.show_wire = True
cylinder.show_all_edges = True