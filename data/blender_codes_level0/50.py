import bpy
import math

# Clear the existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV Sphere with the specified radius
# The sphere is created initially at the world origin (0,0,0)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6)
sphere = bpy.context.active_object
sphere.name = "Sphere_Object"

# Set the sphere's location
sphere.location = (-4.0, -4.0, 0.0)

# Apply rotation of 60 degrees around the X-axis.
# Blender's rotation_euler uses radians.
rotation_radians = math.radians(60.0)
sphere.rotation_euler = (rotation_radians, 0.0, 0.0)

# Optionally, update the scene to ensure transformations are applied
bpy.context.view_layer.update()