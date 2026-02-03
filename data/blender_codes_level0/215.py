import bpy
import math

# Clear existing objects (optional)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified radius and height (depth in Blender)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,  # Default resolution
    radius=1.0,
    depth=4.0,
    location=(0.0, 0.0, 12.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply rotation (20° around Z-axis)
cylinder.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to CYLINDER for accuracy
cylinder.rigid_body.collision_shape = 'CYLINDER'

print(f"Created '{cylinder.name}' at {cylinder.location}, rotated {cylinder.rotation_euler.z:.3f} rad.")