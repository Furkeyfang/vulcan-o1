import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with proper dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 10))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Set dimensions (scale)
cube.scale = (3.0, 3.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Apply 90° rotation on X-axis
cube.rotation_euler = (math.pi/2, 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# Add rigid body properties
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'
cube.rigid_body.mass = 0.0  # Passive objects have infinite mass

# Verify transformation
print(f"Cube created:")
print(f"  Location: {cube.location}")
print(f"  Rotation: {cube.rotation_euler}")
print(f"  Dimensions: {cube.dimensions}")