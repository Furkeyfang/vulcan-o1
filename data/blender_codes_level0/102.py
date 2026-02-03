import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create 2x2x2 cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply transformations from parameter summary
cube.location = (2.0, 5.0, 0.0)
cube.rotation_euler = (0.0, math.radians(45.0), 0.0)  # 45° around Y

# Assign active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
# Use default mass (1.0 kg) and collision shape (CONVEX_HULL)

print(f"Created active cube: {cube.name}")
print(f"  Location: {cube.location}")
print(f"  Rotation (degrees): ({math.degrees(cube.rotation_euler.x):.1f}, {math.degrees(cube.rotation_euler.y):.1f}, {math.degrees(cube.rotation_euler.z):.1f})")