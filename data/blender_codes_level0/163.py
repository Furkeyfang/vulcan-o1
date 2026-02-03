import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=1.5,
    location=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply rotation (45 degrees around Z-axis)
cylinder.rotation_euler[2] = math.radians(45.0)

# Apply translation to final position
cylinder.location = (-2.0, 0.0, 1.0)

# Add passive rigid body physics
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Ensure transformation is applied
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print(f"Cylinder created at {cylinder.location} with rotation {math.degrees(cylinder.rotation_euler[2]):.1f}°")