import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube primitive (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scaling for 3x2x5 dimensions
cube.scale = (1.5, 1.0, 2.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (4.0, 9.0, 7.0)
cube.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0  # Default mass, adjust if needed

# Optional: Add ground plane for context
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'