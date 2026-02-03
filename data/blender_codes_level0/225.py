import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with unit dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply dimensions (scale)
cube.scale = (4.0, 4.0, 1.0)

# Set location and rotation
cube.location = (-10.0, 0.0, 2.0)
cube.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Apply transformations to make them intrinsic
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Add rigid body physics (passive)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Add a simple material for visibility
mat = bpy.data.materials.new(name="Cube_Material")
mat.diffuse_color = (0.8, 0.4, 0.1, 1.0)  # Orange-brown
cube.data.materials.append(mat)

print(f"Created passive cube at {cube.location} with rotation {cube.rotation_euler}")