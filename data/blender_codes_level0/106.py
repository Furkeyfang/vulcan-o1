import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (1m³ at origin)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scale for 1x3x1 dimensions
cube.scale = (1.0, 3.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (0.0, 4.0, -2.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'MESH'
cube.rigid_body.mass = 1.0  # Explicit mass (optional)

# Create ground plane for simulation context
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -5))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set scene gravity for realistic fall
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)