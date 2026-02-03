import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create box with specified dimensions
# Blender's default cube is 2x2x2, so we scale accordingly
bpy.ops.mesh.primitive_cube_add(size=1.0)
box = bpy.context.active_object
box.name = "active_box"

# Set dimensions: (width, depth, height) = (4, 3, 1)
# Scale factors = desired_dimension / 2.0 (since default cube spans -1 to +1)
box.scale = (2.0, 1.5, 0.5)  # 4/2=2, 3/2=1.5, 1/2=0.5
bpy.ops.object.transform_apply(scale=True)  # Apply scale to mesh data

# Set location and rotation
box.location = (-4.0, 7.0, 4.0)
box.rotation_euler = (0.0, math.radians(35.0), 0.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
box.rigid_body.type = 'ACTIVE'

# Set mass proportional to volume (4×3×1 = 12 cubic units)
box.rigid_body.mass = 12.0

print(f"Created active box at {box.location} with rotation {math.degrees(box.rotation_euler[1]):.1f}°")
print(f"Dimensions: {box.dimensions}")