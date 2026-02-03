import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TargetCube"

# Apply dimensions via scale (based on default 2×2×2)
cube.scale = (0.5, 1.0, 3.0)  # Results in 1×2×6
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (6.0, 3.0, -2.0)
cube.rotation_euler = (0.0, math.radians(60.0), 0.0)

# Optional: Add visual materials for clarity
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (0.1, 0.6, 0.9, 1.0)  # Blue color
cube.data.materials.append(mat)

# Add coordinate axes at origin for reference
bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
axis = bpy.context.active_object
axis.name = "WorldOrigin"
axis.empty_display_size = 2.0