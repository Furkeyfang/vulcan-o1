import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=2.0,
    location=(3.0, 0.0, -3.0),
    rotation=(0.0, math.radians(45.0), 0.0)
)

# Get reference to the cylinder
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Assign rigid body properties
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'CYLINDER'

# Verify transformation
print(f"Cylinder created:")
print(f"  Location: {cylinder.location}")
print(f"  Rotation: {cylinder.rotation_euler}")
print(f"  Dimensions: {cylinder.dimensions}")
print(f"  Rigid Body Type: {cylinder.rigid_body.type}")
print(f"  Collision Shape: {cylinder.rigid_body.collision_shape}")