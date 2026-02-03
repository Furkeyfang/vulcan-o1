import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with base dimensions (Blender's default cube is 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)

# Get reference to the cube
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Scale to achieve 2x2x6 dimensions
# Since default cube is 2x2x2, we need to scale Z by 3 to get 6m height
cube.scale = (1.0, 1.0, 3.0)  # (2*1, 2*1, 2*3) = (2, 2, 6)

# Apply scale to make dimensions actual
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (0.0, 7.0, -7.0)

# Set rotation (20 degrees around Z-axis)
# Convert degrees to radians
rotation_rad = math.radians(20.0)
cube.rotation_euler = (0.0, 0.0, rotation_rad)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 10.0  # 10 kg mass

# Optional: Set collision shape to BOX for better performance
cube.rigid_body.collision_shape = 'BOX'

# Update viewport to show changes
bpy.context.view_layer.update()

print(f"Created active cube:")
print(f"  Dimensions: 2.0 × 2.0 × 6.0 m")
print(f"  Location: {cube.location}")
print(f"  Rotation: {math.degrees(cube.rotation_euler.z):.1f}° around Z-axis")
print(f"  Rigid Body: {cube.rigid_body.type}, Mass: {cube.rigid_body.mass} kg")