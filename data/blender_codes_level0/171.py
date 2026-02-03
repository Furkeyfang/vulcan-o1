import bpy
import math

# Clear existing objects (optional for clean scene)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.7,
    depth=3.3,
    location=(2.0, 0.0, -6.0),
    rotation=(0.0, math.radians(25.0), 0.0)
)

cylinder = bpy.context.active_object
cylinder.name = "PassiveCylinder"

# Add rigid body physics and set to passive
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'