import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with given radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location and rotation (Y-axis rotation by 180 degrees)
sphere.location = (-2.0, 4.0, 1.0)
sphere.rotation_euler = (0.0, math.pi, 0.0)  # X, Y, Z in radians

# Assign active rigid body
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # Default mass
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Optional: Set a distinct material color for visibility
mat = bpy.data.materials.new(name="Sphere_Material")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Reddish
if sphere.data.materials:
    sphere.data.materials[0] = mat
else:
    sphere.data.materials.append(mat)

print(f"Sphere created at {sphere.location} with rotation {sphere.rotation_euler}")