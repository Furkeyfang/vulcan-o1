import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube (default 2x2x2 at origin)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Scale to achieve 2×1×3 dimensions (from default 2×2×2)
cube.scale = (1.0, 0.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Move to target location
cube.location = (-2.0, 0.0, 4.0)

# Apply 30-degree rotation about X-axis
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

print(f"Cube created: {cube.name}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (degrees): ({math.degrees(cube.rotation_euler.x):.1f}, {math.degrees(cube.rotation_euler.y):.1f}, {math.degrees(cube.rotation_euler.z):.1f})")
print(f"  Rigid Body Type: {cube.rigid_body.type}")