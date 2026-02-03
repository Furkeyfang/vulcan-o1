import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, -2.0))
ground = bpy.context.active_object
ground.name = "Ground_Plane"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create cube with specified dimensions
# Blender's default cube is 2×2×2, so we scale by half dimensions
scale_factors = (
    4.0 / 2.0,  # X scale
    2.0 / 2.0,  # Y scale  
    2.0 / 2.0   # Z scale
)

bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Active_Cube"

# Apply scaling
cube.scale = scale_factors
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Apply rotation (Y-axis, 75°)
cube.rotation_euler = (0.0, math.radians(75.0), 0.0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Apply translation
cube.location = (1.0, 9.0, -1.0)

# Add active rigid body
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = 2.0  # Default mass (optional)
cube.rigid_body.collision_shape = 'BOX'

# Set up physics scene
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Frame range for simulation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

print(f"Created active cube '{cube.name}'")
print(f"  Dimensions: {cube_dimensions}")
print(f"  Location: {cube.location}")
print(f"  Rotation: {math.degrees(cube.rotation_euler.y):.1f}° around Y-axis")