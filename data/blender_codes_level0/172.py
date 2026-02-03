import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scale transformation to achieve 5x1x2 dimensions
cube.scale = (2.5, 0.5, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-1.0, 8.0, 3.0)
cube.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0  # Default mass
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.2

# Optional: Add visual material for clarity
mat = bpy.data.materials.new(name="ActiveMaterial")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # Blueish color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

print(f"Created active cube at {cube.location}")
print(f"Dimensions: {cube.dimensions}")
print(f"Rotation: {cube.rotation_euler}")