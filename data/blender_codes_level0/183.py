import bpy
import math
from mathutils import Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.4,
    depth=4.1,
    location=(0.0, 0.0, 9.0)
)

cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply 60° rotation around Y-axis (convert to radians)
rotation_euler = Euler((0.0, math.radians(60.0), 0.0), 'XYZ')
cylinder.rotation_euler = rotation_euler

# Add passive rigid body physics
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'
cylinder.rigid_body.mass = 100.0  # Arbitrary mass for passive object

# Update scene and ensure proper transform application
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)