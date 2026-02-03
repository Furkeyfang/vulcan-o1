import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified radius and height
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.3,
    depth=2.7,
    location=(4.0, 0.0, 5.0)
)
cylinder = bpy.context.active_object
cylinder.name = "cylinder_passive"

# Apply rotation of 35 degrees around X-axis (convert to radians)
cylinder.rotation_euler.x = math.radians(35.0)

# Add rigid body physics and set to passive
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'
cylinder.rigid_body.mass = 100.0  # Mass is irrelevant for passive, but set for completeness

print(f"Created passive cylinder: {cylinder.name}")
print(f"  Location: {cylinder.location}")
print(f"  Rotation (degrees): {math.degrees(cylinder.rotation_euler.x)}")