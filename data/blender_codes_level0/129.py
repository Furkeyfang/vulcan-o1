import bpy
import math

# Clear existing objects (optional but good practice)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with base dimensions
# Default Blender cube with size=1 gives 2x2x2 vertices
# We'll scale to achieve exact 2x1x2 dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply scaling for exact dimensions (scale factors multiply the base 2x2x2)
# Target: (2, 1, 2) from base (2, 2, 2) → scale = (1.0, 0.5, 1.0)
cube.scale = (1.0, 0.5, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set final transform
cube.location = (4.0, 0.0, 4.0)
cube.rotation_euler = (0.0, math.radians(33.0), 0.0)

# Add rigid body physics
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Optional: Set display properties for clarity
cube.data.materials.clear()
mat = bpy.data.materials.new(name="Passive_Mat")
mat.diffuse_color = (0.2, 0.6, 0.9, 1.0)  # Blue tint
cube.data.materials.append(mat)

print(f"Created passive cube:")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation (Y): {math.degrees(cube.rotation_euler.y):.1f}°")