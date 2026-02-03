import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = 1.0
ground.rigid_body.restitution = 0.5
ground.data.materials.clear()
mat_ground = bpy.data.materials.new(name="Ground_Material")
mat_ground.diffuse_color = (0.2, 0.4, 0.1, 1.0)
ground.data.materials.append(mat_ground)

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(-5, 5, 2))
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"
sphere.rotation_euler = (0, 0, math.radians(50))  # 50° about Z-axis
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.mass = 5.0
sphere.rigid_body.friction = 0.4
sphere.rigid_body.restitution = 0.7
sphere.data.materials.clear()
mat_sphere = bpy.data.materials.new(name="Sphere_Material")
mat_sphere.diffuse_color = (0.8, 0.2, 0.2, 1.0)
sphere.data.materials.append(mat_sphere)

# Set up world physics
bpy.context.scene.gravity = (0, 0, -9.8)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.data.energy = 2.0

# Add camera for better view
bpy.ops.object.camera_add(location=(15, -15, 10))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(63.4), 0, math.radians(45))
bpy.context.scene.camera = camera

# Set render engine for better visualization
bpy.context.scene.render.engine = 'BLENDER_EEVEE'