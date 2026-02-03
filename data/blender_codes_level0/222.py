import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.9,
    location=(-2.0, 6.0, 9.0)
)
sphere = bpy.context.active_object
sphere.name = "active_sphere"

# Apply 60° rotation around Y-axis
sphere.rotation_euler = (0, math.radians(60.0), 0)

# Add rigid body physics with ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'
sphere.rigid_body.mass = 1.0
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.5

# Ensure proper collision margin (sphere radius will be used)
sphere.rigid_body.use_margin = True
sphere.rigid_body.collision_margin = 0.0

# Create ground plane for physics simulation context
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "ground_plane"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set viewport display for clarity
sphere.display_type = 'SOLID'
ground.display_type = 'WIRE'

print(f"Created active sphere at {sphere.location}")
print(f"Rotation: {math.degrees(sphere.rotation_euler.y):.1f}° around Y-axis")