import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.2,
    location=(8.0, 7.0, -1.0)
)
sphere = bpy.context.active_object
sphere.name = "ActiveSphere"

# Apply 90-degree Y-axis rotation (convert to radians)
sphere.rotation_euler = (0, math.radians(90.0), 0)

# Add Active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # Default mass
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Optionally add ground plane for physics interaction
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, -5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print(f"Created active sphere: radius={sphere_radius}, location={sphere_location}, rotation Y={sphere_rotation_y_degrees}°")