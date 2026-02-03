import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8, location=(2.0, 8.0, 2.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 45° rotation about Z-axis (convert to radians)
sphere.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Add rigid body physics with ACTIVE type
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'

# Adjust collision margin to match visual radius
sphere.rigid_body.collision_margin = 0.0

print(f"Created active sphere: {sphere.name}")
print(f"Radius: 1.8, Location: {sphere.location}, Rotation: {sphere.rotation_euler}")