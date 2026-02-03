import bpy
import math
from mathutils import Vector, Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with specified dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0)
cube = bpy.context.active_object
cube.name = "TiltedCube"

# Set dimensions: Blender scales from unit cube
cube.scale = (3.0, 4.0, 1.0)

# Set location
cube.location = Vector((0.0, -8.0, 1.0))

# Set rotation: 20 degrees around X-axis
# Convert degrees to radians
rotation_rad = math.radians(20.0)
cube.rotation_euler = Euler((rotation_rad, 0.0, 0.0), 'XYZ')

# Apply transformations to make values explicit in object data
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Optional: Add passive rigid body for physics simulations
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'

print(f"Created cube '{cube.name}'")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {math.degrees(cube.rotation_euler.x):.1f}° around X-axis")