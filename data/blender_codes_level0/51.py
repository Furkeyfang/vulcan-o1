import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=5.0,
    location=(3.0, -5.0, 0.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Cylinder_Obstacle"

# Apply rotation (15° around Y-axis)
cylinder.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Add rigid body physics (passive by default)
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'

print(f"Cylinder created at {cylinder.location} with rotation {cylinder.rotation_euler}")