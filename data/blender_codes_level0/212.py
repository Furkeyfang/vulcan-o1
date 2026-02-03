import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with base dimensions (radius=1, height=2)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=2.0,
    location=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "ActiveCylinder"

# Apply scale transformation for correct dimensions
cylinder.scale = (0.8, 0.8, 1.25)  # Based on parameter summary

# Set location and rotation
cylinder.location = (-1.0, 7.0, 6.0)
cylinder.rotation_euler = (0, 0, math.radians(60.0))

# Apply transformations to mesh data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'ACTIVE'
cylinder.rigid_body.mass = 1.0
cylinder.rigid_body.collision_shape = 'MESH'

# Optional: Create ground plane for stability demonstration
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'