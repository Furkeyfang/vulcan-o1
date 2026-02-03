import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add cube with base dimensions (default Blender cube is 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "obstacle_cube"

# Scale to desired dimensions (scale = dimension/2 since default cube is 2 units)
cube.scale = (0.5, 1.0, 3.0)  # 1/2=0.5, 2/2=1.0, 6/2=3.0

# Apply scale to make dimensions actual mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (6.0, 0.0, -2.0)
cube.rotation_euler = (0.0, math.radians(60.0), 0.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Ensure proper display (optional)
cube.display_type = 'SOLID'

print(f"Created passive cube:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (Y): {math.degrees(cube.rotation_euler.y):.1f}°")