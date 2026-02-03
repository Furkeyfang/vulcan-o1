import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.2,
    depth=3.2,
    location=(-4.0, 0.0, 1.0),
    rotation=(0.0, 0.0, math.radians(70.0))
)
cylinder = bpy.context.active_object
cylinder.name = "cylinder_obstacle"

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'CYLINDER'

# Ensure collision shape matches visual (cylinder primitive already axis-aligned)
# No scaling applied, so collision dimensions match object dimensions

print(f"Cylinder created at {cylinder.location}, rotated {70}° on Z-axis")
print(f"Radius: {1.2}, Height: {3.2}, Rigid Body: PASSIVE")