import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.8,
    depth=3.0,
    location=(-3.0, 0.0, -2.0),
    rotation=(0.0, 0.0, 2.0943951)  # 120° in radians
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Assign passive rigid body properties
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Ensure proper display and collision settings
cylinder.display_type = 'SOLID'
bpy.context.view_layer.update()