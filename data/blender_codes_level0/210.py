import bpy
import math

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV sphere with radius 2
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location and rotation
sphere.location = (5.0, 9.0, 0.0)
# Convert 75 degrees to radians for rotation_euler
sphere.rotation_euler = (0, math.radians(75.0), 0)

# Add rigid body physics and set to ACTIVE
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
# Optionally set mass (default is 1.0 kg, but we can be explicit)
sphere.rigid_body.mass = 1.0