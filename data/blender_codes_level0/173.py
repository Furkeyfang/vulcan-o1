import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with base dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Scale to achieve 2×3×3 dimensions
# Default cube is 2×2×2, so we need half scaling factors
cube.scale = (1.0, 1.5, 1.5)

# Apply scale to make dimensions permanent in mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (4.0, 0.0, 4.0)
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add rigid body physics as passive
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.mass = 100.0

# Apply rotation to transform
bpy.ops.object.transform_apply(rotation=True)

# Optional: Add material for visibility
mat = bpy.data.materials.new(name="Cube_Material")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red color
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

print(f"Cube created at {cube.location} with dimensions 2×3×3")
print(f"Rotation: {math.degrees(cube.rotation_euler.x):.1f}° on X-axis")