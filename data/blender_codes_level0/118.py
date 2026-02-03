import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Apply scaling for 1x1x4 dimensions
cube.scale = (0.5, 0.5, 2.0)

# Apply scale transformation to mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (2.0, 8.0, 1.0)
cube.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 4.0  # Volume = 1*1*4 = 4m³
cube.rigid_body.collision_shape = 'BOX'
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.3

# Optional: Add a ground plane for context
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set viewport shading for better visibility
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'
                space.shading.light = 'STUDIO'
                space.shading.color_type = 'MATERIAL'
                break

# Frame the scene
bpy.ops.view3d.view_selected(use_all_regions=False)