import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere with radius 0.6
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(-4.0, 6.0, 0.0))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Apply 60° rotation around X-axis (convert to radians)
sphere.rotation_euler[0] = math.radians(60.0)

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 1.0

# Set scene physics settings (gravity enabled by default)
bpy.context.scene.frame_end = 250  # Extended simulation time

print(f"Created active sphere at {sphere.location}")
print(f"Radius: {sphere.dimensions.x/2:.3f}")
print(f"X-rotation: {math.degrees(sphere.rotation_euler[0]):.1f}°")