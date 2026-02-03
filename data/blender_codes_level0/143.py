import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.5,
    depth=2.0,
    location=(2.0, 0.0, -2.0),
    rotation=(0.0, 0.0, math.radians(10.0))
)
cylinder = bpy.context.active_object
cylinder.name = "passive_cylinder"

# Apply rotation and scale (ensures clean transforms)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Verify properties
print(f"Cylinder created:")
print(f"  Location: {cylinder.location}")
print(f"  Rotation (Euler): {cylinder.rotation_euler}")
print(f"  Radius: {cylinder.dimensions.x/2}")
print(f"  Height: {cylinder.dimensions.z}")