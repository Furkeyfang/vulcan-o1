import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere primitive
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    location=(7.0, 6.0, 3.0)
)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 45° rotation around Y-axis (convert to radians)
sphere.rotation_euler = (0, math.radians(45.0), 0)

# Assign active rigid body
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # default mass
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Optional: Add a simple ground plane for context
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Ensure smooth shading for visual clarity
bpy.ops.object.shade_smooth()