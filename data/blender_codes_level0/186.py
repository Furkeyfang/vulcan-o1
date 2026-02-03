import bpy
import math

# Clear existing mesh objects (optional cleanup)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with radius 0.7
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(-6.0, 6.0, 3.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 15° rotation around Y-axis (convert to radians)
sphere.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0
sphere.rigid_body.collision_shape = 'SPHERE'

# Optional: Set collision margin for stability
sphere.rigid_body.collision_margin = 0.0

# Optional: Add a passive ground plane for simulation testing
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'