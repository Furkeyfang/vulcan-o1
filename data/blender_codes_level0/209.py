import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with base dimensions (Blender's default cube is 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Scale to achieve 3x2x1 dimensions
# Default cube vertices range from -0.5 to 0.5, so scaling by (3,2,1) gives proper dimensions
cube.scale = (3.0, 2.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-6.0, 0.0, 3.0)
cube.rotation_euler = (0.0, 0.0, math.radians(15.0))

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

# Ensure collision shape is BOX (appropriate for cubes)
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set display properties for clarity
cube.show_wire = True
cube.show_all_edges = True

print(f"Created passive cube:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (Z): {math.degrees(cube.rotation_euler.z):.1f}°")
print(f"  Rigid Body Type: {cube.rigid_body.type}")