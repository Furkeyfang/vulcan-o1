import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube (default 2x2x2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "ActiveCube"

# Set dimensions to 3x3x1 (overrides scale automatically)
cube.dimensions = (3.0, 3.0, 1.0)

# Set location
cube.location = (2.0, 5.0, 0.0)

# Set rotation: 20 degrees around Z
cube.rotation_euler = (0.0, 0.0, math.radians(20.0))

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'

# Optional: Set mass based on volume (assuming density 1 kg/m³)
volume = 3.0 * 3.0 * 1.0
cube.rigid_body.mass = volume