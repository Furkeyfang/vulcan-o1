import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with given dimensions
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=4.0,
    location=(-6.0, 6.0, 0.0),
    rotation=(math.radians(30.0), 0.0, 0.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Active_Cylinder"

# Assign active rigid body properties
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'ACTIVE'
cylinder.rigid_body.mass = 10.0  # Default mass, can be adjusted
cylinder.rigid_body.friction = 0.5
cylinder.rigid_body.restitution = 0.1

# Ensure viewport displays physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print(f"Cylinder created at {cylinder.location} with rotation {cylinder.rotation_euler}")