import bpy
import math

# Clear existing objects (optional, but good for a clean slate)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cylinder with radius 1 and depth 5 (height along local Z)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=5.0,
    location=(-11.0, 0.0, -2.0),
    rotation=(0.0, 0.0, math.radians(60.0))
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Add a passive rigid body component
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'