import bpy
import math
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,
    location=(0.0, 3.0, 0.0),
    segments=32,
    ring_count=16
)

sphere = bpy.context.active_object
sphere.name = "positioned_sphere"

# Apply 90° rotation about Z-axis
rotation_angle = math.radians(90.0)
rotation_matrix = Matrix.Rotation(rotation_angle, 4, 'Z')
sphere.matrix_world @= rotation_matrix

# Alternative: Set rotation directly (ensures exact 90° about global Z)
sphere.rotation_euler = (0.0, 0.0, rotation_angle)

# Update scene
bpy.context.view_layer.update()

# Verification output
print(f"Sphere created at: {sphere.location}")
print(f"Sphere rotation (radians): {sphere.rotation_euler}")
print(f"Sphere scale: {sphere.scale}")