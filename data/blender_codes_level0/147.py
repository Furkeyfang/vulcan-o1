import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=2.0,
    depth=3.0,
    location=(-7.0, 0.0, 2.0),
    rotation=(math.radians(25.0), 0.0, 0.0)
)

cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Add rigid body physics (passive)
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Ensure proper shading
bpy.ops.object.shade_smooth()

print(f"Created passive cylinder: {cylinder.name}")
print(f"Location: {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler.x):.1f}° on X-axis")