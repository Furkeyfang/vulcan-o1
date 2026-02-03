import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube at origin
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scaling for dimensions 1×4×3 (X, Y, Z)
cube.scale = (0.5, 2.0, 1.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set final location and rotation
cube.location = (-1.0, 7.0, -3.0)
cube.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'BOX'

# Apply visual material for clarity
mat = bpy.data.materials.new(name="ActiveCube_Material")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
cube.data.materials.append(mat)

print(f"Created active cube:")
print(f"  Location: {cube.location}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Rotation: {math.degrees(cube.rotation_euler.z):.1f}° Z-axis")
print(f"  Rigid Body: {cube.rigid_body.type}")