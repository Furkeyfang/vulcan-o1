import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with base dimensions 1x1x1 (will scale)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply dimensions (scale) - Blender's default cube is 2x2x2, so we adjust
# To get 1x2x2 from a default 2x2x2 cube, we scale by (0.5, 1.0, 1.0)
cube.scale = (0.5, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (10.0, 0.0, 1.0)
cube.rotation_euler = (0.0, 0.0, math.radians(60.0))

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Optional: Set collision shape to BOX (default for cubes)
cube.rigid_body.collision_shape = 'BOX'

print(f"Created passive cube: {cube.name}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (Z): {math.degrees(cube.rotation_euler.z):.1f}°")