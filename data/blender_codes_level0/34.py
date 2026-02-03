import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV Sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(-5.0, 3.0, 2.0))

# Get reference to the created sphere
sphere = bpy.context.active_object
sphere.name = "Target_Sphere"

# Apply rotation of 50 degrees around Z-axis (convert to radians)
sphere.rotation_euler = (0.0, 0.0, math.radians(50.0))

# Optionally, set the object origin to its center (already by default)
# No further physics properties are added as not specified.