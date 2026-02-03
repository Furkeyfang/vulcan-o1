import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with specified dimensions
# Default Blender cube is 2x2x2, scale by half dimensions
cube = bpy.ops.mesh.primitive_cube_add(
    size=2.0,
    location=(6.0, 0.0, -3.0),
    scale=(0.5, 1.0, 2.0)  # Scale to achieve 1x2x4 dimensions
)

# Get reference to the active object
cube_obj = bpy.context.active_object
cube_obj.name = "Passive_Cube"

# Apply Z-axis rotation (45 degrees)
cube_obj.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Add rigid body physics and set to PASSIVE
bpy.ops.rigidbody.object_add()
cube_obj.rigid_body.type = 'PASSIVE'

# Optional: Set display properties for clarity
cube_obj.display_type = 'SOLID'
bpy.context.object.data.materials.clear()

print(f"Created passive cube:")
print(f"  Dimensions: 1.0 × 2.0 × 4.0 m")
print(f"  Location: {cube_obj.location}")
print(f"  Rotation: {math.degrees(cube_obj.rotation_euler.z):.1f}° on Z-axis")