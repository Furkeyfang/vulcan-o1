import bpy
import math

# Clear existing mesh objects for a clean start
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the UV sphere primitive with the specified radius
# The primitive is created at the world origin (0,0,0) by default
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.4, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply translation: move sphere to specified location
sphere.location = (2.0, -2.0, 8.0)

# Apply rotation: 60 degrees about the X-axis (convert to radians)
sphere.rotation_euler = (math.radians(60.0), 0.0, 0.0)

# Optional: Update the viewport to show the changes
bpy.context.view_layer.update()