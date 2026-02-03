import bpy
import math
from mathutils import Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=6.0,
    location=(-1.0, 0.0, 10.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply rotation: 30 degrees about Z-axis
# Convert to radians and create rotation Euler
rotation_rad = math.radians(30.0)
cylinder.rotation_euler = Euler((0.0, 0.0, rotation_rad), 'XYZ')

# Add rigid body physics with passive type
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to mesh for accurate interactions
cylinder.rigid_body.collision_shape = 'MESH'

print(f"Created {cylinder.name} at {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler.z):.1f}° about Z-axis")