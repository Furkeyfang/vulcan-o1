import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with 32 segments/rings for smooth appearance
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=2.7,
    location=(0, 8, 0),
    rotation=(0, math.radians(30), 0)
)

# Name the sphere object
sphere = bpy.context.active_object
sphere.name = "sphere_01"

# Ensure correct scale
sphere.scale = (1.0, 1.0, 1.0)

# Apply rotation and scale transformations
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Update scene
bpy.context.view_layer.update()