import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create floor plane
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -10))
floor = bpy.context.active_object
floor.name = "Floor"
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'

# Create cube with specified dimensions
# Default cube is 2x2x2, so we scale by (1,2,1) to get 2x4x2
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))
cube = bpy.context.active_object
cube.name = "Cube"
cube.scale = (1.0, 2.0, 1.0)  # Scale Y by 2 to get depth=4 (since base size=2)
bpy.ops.object.transform_apply(scale=True)  # Apply scale to have true dimensions

# Set location and rotation
cube.location = (5.0, 9.0, -5.0)
cube.rotation_euler = (math.radians(20.0), 0, 0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
# Optional: set mass explicitly (default is calculated from volume and density)
# cube.rigid_body.mass = 1.0

# Set scene gravity to default -9.8 along Z (already default, but explicit)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.8)

# Optional: Set frame range for animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250