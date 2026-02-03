import bpy
import math

# Clear existing objects (optional, to start fresh)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cylinder primitive
# The default cylinder in Blender has 32 vertices, radius 1, depth 2, and is aligned along the Z-axis.
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.9, depth=2.8, location=(3, 0, 12))
cylinder = bpy.context.active_object
cylinder.name = "Passive_Cylinder"

# Rotate 45 degrees around Z-axis. Convert degrees to radians.
cylinder.rotation_euler = (0, 0, math.radians(45))

# Add rigid body physics and set to passive
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'PASSIVE'