import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.0,
    location=(1.0, 6.0, 1.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Active_Cylinder"

# Apply rotation (60 degrees around X-axis)
cylinder.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'ACTIVE'
cylinder.rigid_body.mass = 10.0  # Reasonable mass for size
cylinder.rigid_body.friction = 0.5
cylinder.rigid_body.restitution = 0.2

# Create floor plane for simulation stability
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
floor = bpy.context.active_object
floor.name = "Floor"

# Add passive rigid body
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'
floor.rigid_body.friction = 0.5
floor.rigid_body.restitution = 0.2

# Set up world physics
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Frame settings for animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250