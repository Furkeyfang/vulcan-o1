import bpy
import mathutils

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default cube (2x2x2m)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Passive_Cube"

# Apply scaling for target dimensions (1x2x2)
# Default cube vertices at ±0.5 => scale (1,1,1) gives 1x1x1m
# Target: X=1.0m (scale 0.5), Y=2.0m (scale 1.0), Z=2.0m (scale 1.0)
cube.scale = (0.5, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Set location and rotation
cube.location = (1.0, 0.0, 5.0)
cube.rotation_euler = (0.0, 0.0, math.radians(45.0))

# Apply rotation transformation
bpy.ops.object.transform_apply(rotation=True)

# Add rigid body physics as PASSIVE
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'

# Verify final properties
print(f"Cube created: {cube.name}")
print(f"  Dimensions: {cube.dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {cube.rotation_euler}")
print(f"  Rigid Body: {cube.rigid_body.type}")