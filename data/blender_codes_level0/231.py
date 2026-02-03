import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.1,
    depth=4.0,
    location=(6.0, 0.0, -10.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply 45° rotation around Y-axis (convert to radians)
cylinder.rotation_euler = (0, math.radians(45.0), 0)

# Set as passive rigid body for physics simulations
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Update scene to ensure transformations are applied
bpy.context.view_layer.update()

print(f"Created {cylinder.name} at location {cylinder.location}")
print(f"Radius: 1.1, Height: 4.0, Rotation: 45° around Y-axis")