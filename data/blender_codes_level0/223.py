import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with default orientation (axis along Z)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=2.0,
    depth=1.0,
    location=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply transformations
cylinder.location = (4.0, 0.0, 10.0)
cylinder.rotation_euler = (math.radians(90.0), 0.0, 0.0)  # 90° around X-axis

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Optional: Set collision margin
cylinder.rigid_body.collision_margin = 0.0

print(f"Created {cylinder.name} at {cylinder.location}")
print(f"Rotation: {cylinder.rotation_euler}")
print(f"Rigid Body Type: {cylinder.rigid_body.type}")