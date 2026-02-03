import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with radius 3
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.0)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location
sphere.location = (-6.0, 12.0, 2.0)

# Apply rotation: 15 degrees around Y-axis
sphere.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'