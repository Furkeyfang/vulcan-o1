import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.7,
    depth=3.5,
    location=(0, 0, 0),
    rotation=(0, 0, 0)
)
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Apply transformations in correct order
# 1. Rotation around Z-axis (60 degrees)
cylinder.rotation_euler[2] = math.radians(60.0)

# 2. Translation to target location
cylinder.location = (-5.0, 0.0, -7.0)

# Update object transformations
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Configure as passive rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'
cylinder.rigid_body.collision_shape = 'MESH'

# Set visual properties (optional, for clarity)
cylinder.data.materials.clear()
mat = bpy.data.materials.new(name="Cylinder_Material")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # Blue color
cylinder.data.materials.append(mat)

print(f"Cylinder created: {cylinder.name}")
print(f"Location: {cylinder.location}")
print(f"Rotation: {math.degrees(cylinder.rotation_euler[2]):.1f}° around Z-axis")