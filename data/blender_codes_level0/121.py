import bpy
import math

# Clear existing scene (optional, ensures a clean start)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add a UV sphere with the specified radius
# Default segments and rings are fine for a simple sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.0, location=(8.0, 0.0, 0.0))
sphere = bpy.context.active_object
sphere.name = "passive_sphere"

# Apply 45-degree rotation around the Z-axis
# Rotation in Blender is in radians
sphere.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Add a passive rigid body component
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'PASSIVE'
# Ensure collision shape is appropriate (MESH for a sphere is accurate but heavier; SPHERE is efficient)
sphere.rigid_body.collision_shape = 'SPHERE'