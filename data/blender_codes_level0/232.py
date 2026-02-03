import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (1, 1, 0.1)  # Make it thin
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create the main cube with default Blender cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply scaling to achieve 5×1×3 dimensions
cube.scale = (2.5, 0.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (-4, 9, 4)
cube.rotation_euler = (math.radians(30), 0, 0)

# Add active rigid body properties
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 5.0  # Reasonable mass for volume ~15 m³
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.3

# Set up world physics
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)

# Optional: Frame the view
bpy.context.scene.camera.location = (10, -15, 10)
bpy.context.scene.camera.rotation_euler = (
    math.radians(60),
    0,
    math.radians(30)
)