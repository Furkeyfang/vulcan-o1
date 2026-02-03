import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.7, location=(3.0, 9.0, 7.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply rotation: 15 degrees around X-axis
sphere.rotation_euler.x = math.radians(15.0)

# Add active rigid body for physics simulation
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'