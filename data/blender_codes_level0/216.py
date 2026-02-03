import bpy
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Set dimensions via scale (from 2x2x2 to 5x2x1)
cube.scale = (2.5, 1.0, 0.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (2.0, 9.0, -4.0)
cube.rotation_euler = (0, radians(35.0), 0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'BOX'
cube.rigid_body.mass = 1.0  # Default mass

# Optional: Verify dimensions
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube location: {cube.location}")
print(f"Cube rotation (Y): {cube.rotation_euler.y} rad")