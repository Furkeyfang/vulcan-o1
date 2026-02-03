import bpy
import math
from mathutils import Vector, Euler

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube with default dimensions (2×2×2)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply transformation based on parameters
cube.location = Vector((-2.0, 0.0, -5.0))
cube.scale = Vector((1.5, 1.0, 1.0))
cube.rotation_euler = Euler((0.0, 0.0, 15.0 * math.pi / 180.0), 'XYZ')

# Add rigid body physics with PASSIVE type
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Verify dimensions
print(f"Cube created at: {cube.location}")
print(f"Cube dimensions: {cube.dimensions}")
print(f"Cube scale: {cube.scale}")
print(f"Rigid body type: {cube.rigid_body.type}")