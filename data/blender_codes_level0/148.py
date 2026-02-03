import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create default floor plane for physics context
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'

# Create the 3×3×3 cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(2.0, 9.0, 2.0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Scale to achieve 3m dimensions (default cube is 2m, scale by 1.5)
cube.scale = (1.5, 1.5, 1.5)

# Apply scale transformation
bpy.ops.object.transform_apply(scale=True)

# Rotate 45° around Y-axis
cube.rotation_euler = (0.0, math.radians(45.0), 0.0)

# Add active rigid body properties
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 1.0
cube.rigid_body.friction = 0.5
cube.rigid_body.restitution = 0.0

# Set up physics world with default gravity
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = bpy.data.collections.new("PhysicsCollection")
bpy.context.scene.rigidbody_world.collection.objects.link(cube)
bpy.context.scene.rigidbody_world.collection.objects.link(floor)

# Verify transformations
print(f"Cube created at location: {cube.location}")
print(f"Cube rotation (degrees): {math.degrees(cube.rotation_euler.y)}")
print(f"Cube dimensions: {cube.dimensions}")