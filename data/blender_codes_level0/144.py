import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with unit dimensions (Blender default is 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0)

# Get reference to the cube
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Set dimensions (scale from unit cube)
cube.dimensions = (2.0, 3.0, 2.0)

# Apply scale to make dimensions permanent
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-3.0, 7.0, 3.0)
cube.rotation_euler = (math.radians(35.0), 0.0, 0.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0
cube.rigid_body.collision_shape = 'BOX'

# Update scene
bpy.context.view_layer.update()

print(f"Created active cube '{cube.name}'")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {[math.degrees(r) for r in cube.rotation_euler]}")
print(f"  Rigid Body: {cube.rigid_body.type}, Mass: {cube.rigid_body.mass}")