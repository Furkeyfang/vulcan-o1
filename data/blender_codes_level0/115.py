import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube (default 2m cube)
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply scaling to achieve 2x3x1 dimensions
cube.scale = (1.0, 1.5, 0.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Set location and rotation
cube.location = (-5.0, 0.0, 2.0)
cube.rotation_euler = (0.0, math.radians(35.0), 0.0)

# Add rigid body properties
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.mass = 50.0