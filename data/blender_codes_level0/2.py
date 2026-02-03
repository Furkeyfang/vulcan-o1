import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube with dimensions 2x2x2
# Default cube in Blender is 2x2x2, but its scale is (1,1,1) meaning 2 units in each direction
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Target_Cube"

# Set location: (5, 0, 0)
cube.location = (5.0, 0.0, 0.0)

# Rotate 45° about Y-axis
# Convert degrees to radians
rot_y_rad = math.radians(45.0)
cube.rotation_euler = (0.0, rot_y_rad, 0.0)

# Verify dimensions: scale should remain (1,1,1) for a 2x2x2 cube
cube.scale = (1.0, 1.0, 1.0)

# Optionally, set display to show transformations clearly
bpy.context.space_data.overlay.show_extra_indices = True