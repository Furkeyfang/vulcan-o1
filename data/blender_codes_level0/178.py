import bpy
import math
from mathutils import Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.6,
    location=(2.0, 8.0, 6.0)
)
sphere = bpy.context.active_object
sphere.name = "ActiveSphere"

# Apply 90° rotation around Z-axis (convert degrees to radians)
rotation_radians = math.radians(90.0)
sphere.rotation_euler = Euler((0.0, 0.0, rotation_radians), 'XYZ')

# Add rigid body physics with ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'
sphere.rigid_body.mass = 1.0
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Verify transformation
print(f"Sphere created at: {sphere.location}")
print(f"Sphere rotation (radians): {sphere.rotation_euler}")
print(f"Rigid body type: {sphere.rigid_body.type}")