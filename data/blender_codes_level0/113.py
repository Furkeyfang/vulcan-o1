import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with radius 1, depth 1 (default axis along Z)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=1.0,
    location=(4.0, 0.0, 4.0)
)
cylinder = bpy.context.active_object
cylinder.name = "passive_cylinder"

# Rotate 90 degrees on X-axis (convert to radians)
cylinder.rotation_euler[0] = math.radians(90.0)

# Add rigid body physics (passive - static)
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Ensure proper scale
cylinder.scale = (1.0, 1.0, 1.0)

# Update transformations
bpy.context.view_layer.update()