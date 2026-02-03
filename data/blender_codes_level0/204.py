import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.0,
    location=(4.0, 7.0, -3.0)
)
cylinder = bpy.context.active_object
cylinder.name = "ActiveCylinder"

# Apply 45-degree rotation around Y-axis (convert to radians)
cylinder.rotation_euler = (0, math.radians(45.0), 0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'ACTIVE'
cylinder.rigid_body.mass = 1.0  # Default mass
cylinder.rigid_body.friction = 0.5
cylinder.rigid_body.restitution = 0.1

# Ensure visual smoothness
bpy.ops.object.shade_smooth()

# Set up a ground plane for reference
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print(f"Cylinder created at {cylinder.location}")
print(f"Cylinder rotation (degrees): {math.degrees(cylinder.rotation_euler.y)}")