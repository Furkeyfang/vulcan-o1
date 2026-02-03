import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube primitive (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2)

# Get reference to the active object
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply transformations from parameter summary
cube.location = (0.0, 8.0, -8.0)
cube.rotation_euler = (0.0, 0.0, math.radians(25.0))
cube.scale = (0.5, 1.5, 2.0)

# Apply scale to avoid distortion in physics calculations
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 12.0  # 1*3*4 = 12 cubic meters with density 1
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.2
cube.rigid_body.linear_damping = 0.04
cube.rigid_body.angular_damping = 0.1

# Verify dimensions
dimensions = [cube.dimensions.x, cube.dimensions.y, cube.dimensions.z]
print(f"Created cube with dimensions: {dimensions}")