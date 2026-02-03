import bpy
import math

# Clear existing scene for clean execution
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=2.0,
    depth=1.0,
    location=(0.0, 0.0, -5.0),
    rotation=(0.0, math.radians(45.0), 0.0)
)

cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Add rigid body physics with passive type
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Optional: Set collision margin for stability
cylinder.rigid_body.collision_margin = 0.0

print(f"Created {cylinder.name} at {cylinder.location} with rotation {cylinder.rotation_euler}")
print(f"Radius: 2.0, Height: 1.0, Rigid Body Type: {cylinder.rigid_body.type}")