import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with given dimensions
# Blender's default cylinder has radius=1, height=2, so we scale accordingly
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=1.0,
    location=(0, 0, 0)
)

cylinder = bpy.context.active_object
cylinder.name = "Target_Cylinder"

# Set location
cylinder.location = (4.0, 4.0, 4.0)

# Set rotation (90° around X-axis)
# Convert degrees to radians for rotation_euler
cylinder.rotation_euler = (math.radians(90.0), 0, 0)

# Apply rotation to mesh data for clean transformation
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

print(f"Cylinder created at {cylinder.location} with rotation {cylinder.rotation_euler}")