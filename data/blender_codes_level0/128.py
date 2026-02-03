import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create default cube (2×2×2m)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube_1x5x1"

# Apply dimensions via scale (default cube is 2m per side)
# To get 1m in X: 1/2 = 0.5, 5m in Y: 5/2 = 2.5, 1m in Z: 1/2 = 0.5
cube.scale = (0.5, 2.5, 0.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (2.0, 9.0, 2.0)
cube.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 2500.0  # 500 kg/m³ × 5 m³

# Optional: Add ground plane for simulation
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Ground"
bpy.ops.rigidbody.object_add()
plane.rigid_body.type = 'PASSIVE'

# Set gravity to realistic Earth value (optional)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)