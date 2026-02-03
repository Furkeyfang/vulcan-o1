import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default dimensions
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "PassiveCube"

# Set rotation (30° about X-axis)
cube.rotation_euler = (math.radians(30), 0, 0)

# Add passive rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Verify properties
print(f"Cube created at {cube.location}")
print(f"Cube rotation (degrees): {[math.degrees(r) for r in cube.rotation_euler]}")
print(f"Rigid body type: {cube.rigid_body.type}")