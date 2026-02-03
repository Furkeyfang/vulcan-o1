import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.6,
    depth=2.4,
    location=(1.0, 0.0, 1.0),
    rotation=(math.radians(90.0), 0.0, 0.0)
)

# Reference the active object
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Verify transformations
print(f"Cylinder created at: {cylinder.location}")
print(f"Cylinder rotation (radians): {cylinder.rotation_euler}")
print(f"Cylinder dimensions: Radius=0.6, Height=2.4")