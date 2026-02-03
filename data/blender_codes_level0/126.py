import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder with specified dimensions
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.75,
    depth=2.5,
    location=(1.0, 5.0, -4.0)
)
cylinder = bpy.context.active_object
cylinder.name = "Active_Cylinder"

# Apply rotation (40° about Y-axis)
cylinder.rotation_euler = (0.0, math.radians(40.0), 0.0)

# Make cylinder an active rigid body
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'ACTIVE'
cylinder.rigid_body.mass = 1.0
cylinder.rigid_body.friction = 0.5
cylinder.rigid_body.restitution = 0.3

# Ensure proper collision shape
cylinder.rigid_body.collision_shape = 'MESH'

# Enable physics visualization (optional)
bpy.context.scene.rigidbody_world.enabled = True