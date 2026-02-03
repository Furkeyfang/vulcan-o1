import bpy
import math

# Clear existing objects (optional, for a clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create the cylinder with specified radius
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.9,
    depth=3.6,
    location=(3.0, 0.0, -8.0)
)

# Get the reference to the newly created cylinder
cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Apply the 45-degree rotation around the Z-axis
cylinder.rotation_euler = (0, 0, math.radians(45.0))

# Optional: Set the object as a passive rigid body for future physics simulation
# bpy.ops.rigidbody.object_add()
# cylinder.rigid_body.type = 'PASSIVE'