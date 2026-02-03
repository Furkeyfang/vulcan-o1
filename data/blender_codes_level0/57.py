import bpy
from math import radians

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0)
cube = bpy.context.active_object
cube.name = "rectangular_prism"

# Apply non-uniform scaling for 2×5×1 dimensions
# Default cube dimensions: 2×2×2, so scale factors:
# X: 2.0/2.0 = 1.0, Y: 5.0/2.0 = 2.5, Z: 1.0/2.0 = 0.5
cube.scale = (1.0, 2.5, 0.5)

# Apply scale to mesh data to avoid distortion
bpy.ops.object.transform_apply(scale=True)

# Set location
cube.location = (-5.0, 2.0, 0.0)

# Set rotation (25° around Y-axis)
cube.rotation_euler = (0.0, radians(25.0), 0.0)

# Optional: Set display properties
cube.data.name = "RectangularPrismMesh"
cube.show_wire = True
cube.show_all_edges = True

print(f"Created {cube.name} at {cube.location} with rotation {cube.rotation_euler}")