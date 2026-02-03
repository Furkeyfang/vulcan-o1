import bpy
from mathutils import Matrix
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with default dimensions (2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "TargetCube"

# Scale to desired dimensions (5,1,1) from default (1,1,1)
cube.scale = (5.0, 1.0, 1.0)

# Apply scale transformation to mesh data
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (6.0, 1.0, 0.0)

# Set rotation (15° around Y-axis)
cube.rotation_euler = (0.0, math.radians(15.0), 0.0)

# Optional: Add passive rigid body for physics (if needed later)
# bpy.ops.rigidbody.object_add()
# cube.rigid_body.type = 'PASSIVE'

print(f"Cube '{cube.name}' created at {cube.location} with rotation {cube.rotation_euler}")