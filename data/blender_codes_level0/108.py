import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder with radius 0.5 and depth 3 (Blender's cylinder depth is along local Z)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,
    depth=3.0,
    location=(0.0, 7.0, 3.0)
)
cylinder = bpy.context.active_object
cylinder.name = "ActiveCylinder"

# Rotate 120° about global Z-axis (convert degrees to radians)
rotation_rad = math.radians(120.0)
cylinder.rotation_euler = (0.0, 0.0, rotation_rad)

# Add Active rigid body component
bpy.ops.rigidbody.object_add()
cylinder.rigid_body.type = 'ACTIVE'
cylinder.rigid_body.mass = 1.0  # default mass
cylinder.rigid_body.collision_shape = 'MESH'  # matches the cylinder geometry accurately

# Ensure the cylinder is visible and rendered
cylinder.display_type = 'TEXTURED'

print(f"Cylinder created at {cylinder.location} with rotation {cylinder.rotation_euler}")