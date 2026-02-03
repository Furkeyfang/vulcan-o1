import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.6,
    depth=2.9,
    location=(-3.0, 0.0, -4.0),
    rotation=(math.radians(15.0), 0.0, 0.0)
)

cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Add rigid body physics with passive type
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Set collision margin for stability
cylinder.rigid_body.collision_margin = 0.0

# Enable visibility of rigid body in viewport
cylinder.show_rigid_body = True

print(f"Created passive cylinder: {cylinder.name}")
print(f"Location: {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler.x):.1f}° on X-axis")