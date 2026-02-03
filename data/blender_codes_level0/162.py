import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.7, location=(0, 11, 0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 30° rotation around Y-axis
sphere.rotation_euler[1] = math.radians(30.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0  # Default mass
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Ensure proper viewport display
bpy.context.view_layer.update()
print(f"Created {sphere.name} with radius {sphere.dimensions.x/2}")