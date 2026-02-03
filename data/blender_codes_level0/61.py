import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TaskCube"

# Apply scale to achieve 1×1×3 dimensions
cube.scale = (0.5, 0.5, 1.5)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (7.0, 2.0, 0.0)
cube.rotation_euler = (math.radians(90.0), 0.0, 0.0)

# Optional: Add wireframe viewport display for clarity
cube.display_type = 'WIRE'
cube.show_wire = True
cube.show_all_edges = True