import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
# Default sphere has radius 1.0, so we scale by 1.8
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,  # Will be scaled
    location=(0, 0, 0),
    scale=(1.8, 1.8, 1.8)
)
sphere = bpy.context.active_object
sphere.name = "TargetSphere"

# Apply rotation (45° about Z-axis)
sphere.rotation_euler = (0, 0, math.radians(45.0))

# Apply location
sphere.location = (2.0, -6.0, 2.0)

# Apply transforms to make transformations explicit in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Optional: Add rigid body physics for future simulations
bpy.ops.rigidbody.object_add()
sphere.rigid_body.mass = 1.0
sphere.rigid_body.collision_shape = 'SPHERE'