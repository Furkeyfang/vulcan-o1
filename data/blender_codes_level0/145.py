import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube primitive (default 2x2x2 at origin)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "cube_passive"

# Apply scale to achieve 4x1x2 dimensions
cube.scale = (2.0, 0.5, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (1.0, 0.0, -4.0)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)

# Add rigid body physics (Passive)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set display to show wireframe for clarity
cube.show_wire = True
cube.show_all_edges = True