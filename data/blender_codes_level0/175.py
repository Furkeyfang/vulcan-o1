import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.1,
    depth=2.2,
    location=(7.0, 0.0, -2.0),
    rotation=(0, 0, math.radians(45.0))
)
cylinder = bpy.context.active_object
cylinder.name = "passive_cylinder"

# Assign passive rigid body property
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

print(f"Created passive cylinder '{cylinder.name}'")
print(f"  Radius: {cylinder.dimensions.x/2}")
print(f"  Height: {cylinder.dimensions.z}")
print(f"  Location: {cylinder.location}")
print(f"  Rotation: {math.degrees(cylinder.rotation_euler.z)}° about Z-axis")