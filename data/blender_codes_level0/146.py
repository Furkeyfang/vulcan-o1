import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with radius 1.0
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply transformations from parameter summary
sphere.location = (5.0, 8.0, 5.0)
sphere.rotation_euler = (0.0, 0.0, 2.09439510239)  # 120 degrees in Z

# Add rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'
sphere.rigid_body.use_margin = True
sphere.rigid_body.collision_margin = 0.0  # Exact sphere radius

# Optional: Set mass based on volume (density ~1)
# Volume = 4/3 * π * r^3 = 4.18879 m³
# Mass = density * volume = 1.0 * 4.18879 ≈ 4.19 kg
sphere.rigid_body.mass = 4.18879

# Ensure smooth shading for visual clarity
bpy.ops.object.shade_smooth()