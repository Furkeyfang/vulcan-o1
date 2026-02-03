import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.5,
    depth=2.0,
    location=(-3.0, 0.0, 8.0),
    rotation=(0.0, math.radians(15.0), 0.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Assign passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'