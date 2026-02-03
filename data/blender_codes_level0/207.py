import bpy
import math
from mathutils import Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,  # Smooth default resolution
    radius=1.2,
    depth=3.0,
    location=(1.0, 0.0, -6.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply 25-degree rotation around Y-axis
# Convert degrees to radians for Euler rotation
rotation_rad = math.radians(25.0)
cylinder.rotation_euler = Euler((0.0, rotation_rad, 0.0), 'XYZ')

# Add rigid body physics with PASSIVE type
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'  # Use exact mesh for collision

# Optional: Set collision margin for stability
cylinder.rigid_body.collision_margin = 0.0

# Validate transformations
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
print(f"Created cylinder at {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler.y):.1f}° around Y-axis")