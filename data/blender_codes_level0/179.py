import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=2.2,
    depth=1.8,
    location=(-5.0, 0.0, 1.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply rotation (15 degrees around X-axis)
cylinder.rotation_euler.x = math.radians(15.0)

# Add passive rigid body property
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'CYLINDER'

# Ensure transformations are applied
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print("Cylinder created successfully at (-5, 0, 1) with 15° X-axis rotation.")