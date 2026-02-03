import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere primitive (default segments=32, rings=16)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,
    location=(0.0, 3.0, 2.0),
    scale=(1.0, 1.0, 1.0)
)
sphere = bpy.context.active_object
sphere.name = "Passive_Sphere"

# Apply 90-degree rotation around Z-axis (convert degrees to radians)
sphere.rotation_euler = (0.0, 0.0, math.radians(90.0))

# Add rigid body physics and set to passive
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'PASSIVE'

# Optional: Set mass (not strictly needed for passive, but good practice)
sphere.rigid_body.mass = 1.0

print(f"Created passive sphere '{sphere.name}'")
print(f"  Location: {sphere.location}")
print(f"  Rotation: {tuple(math.degrees(r) for r in sphere.rotation_euler)}")
print(f"  Radius: {sphere.dimensions.x / 2.0}")