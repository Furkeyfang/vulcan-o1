import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.5,
    depth=4.0,
    location=(-1.0, 0.0, -1.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply rotation (30° around X-axis)
cylinder.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'
cylinder.rigid_body.use_margin = True
cylinder.rigid_body.collision_margin = 0.0

# Ensure smooth shading for better visualization
bpy.ops.object.shade_smooth()

print(f"Created passive cylinder at {cylinder.location}")
print(f"Rotation: {cylinder.rotation_euler}")