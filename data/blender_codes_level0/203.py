import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with radius 1.0
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0)
sphere = bpy.context.active_object
sphere.name = "Passive_Sphere"

# Set location
sphere.location = (-2.0, 0.0, 6.0)

# Set rotation: 30 degrees around Z-axis (convert to radians)
sphere.rotation_euler = (0.0, 0.0, math.radians(30.0))

# Add rigid body physics with PASSIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'PASSIVE'