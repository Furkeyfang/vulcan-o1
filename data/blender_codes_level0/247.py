import bpy
import math

# Clear existing objects (optional, for a clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified radius and height
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,            # Smoothness
    radius=1.8,
    depth=3.5,
    location=(-10.0, 0.0, 6.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Rotate 25 degrees around X-axis (convert to radians)
cylinder.rotation_euler[0] = math.radians(25.0)

# Add rigid body physics, set to PASSIVE (static)
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'  # More accurate than 'CONVEX_HULL' for a cylinder