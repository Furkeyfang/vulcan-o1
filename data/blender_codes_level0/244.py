import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default 2x2x2 dimensions
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Set dimensions to 4x3x1
cube.dimensions = (4.0, 3.0, 1.0)

# Apply scale to make dimensions permanent
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (-2.0, 10.0, -10.0)

# Set rotation (convert 30 degrees to radians)
cube.rotation_euler = (math.radians(30.0), 0.0, 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Set rigid body mass based on volume (assuming density 1 kg/m³)
volume = 4.0 * 3.0 * 1.0
cube.rigid_body.mass = volume

print(f"Created active cube: {cube.name}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (degrees): ({math.degrees(cube.rotation_euler.x):.1f}, 0, 0)")