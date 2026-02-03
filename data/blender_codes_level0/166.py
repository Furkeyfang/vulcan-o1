import bpy
import math

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere with specified radius
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1)
sphere = bpy.context.active_object
sphere.name = "Active_Sphere"

# Set location
sphere.location = (3.0, 8.0, -2.0)

# Apply rotation (60° around Z-axis)
sphere.rotation_euler = (0.0, 0.0, math.radians(60.0))

# Add active rigid body physics
bpy.ops.rigidbody.object_add()
sphere.rigid_body.type = 'ACTIVE'
sphere.rigid_body.collision_shape = 'SPHERE'
sphere.rigid_body.mass = 1.0
sphere.rigid_body.friction = 0.5
sphere.rigid_body.restitution = 0.8

# Ensure collision geometry matches visual
sphere.rigid_body.use_margin = True
sphere.rigid_body.collision_margin = 0.0

# Add material for visualization
mat = bpy.data.materials.new(name="Sphere_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Create principled BSDF node
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.2, 1.0)  # Red color
bsdf.inputs['Roughness'].default_value = 0.3

# Create material output node
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (400, 0)

# Link nodes
links = mat.node_tree.links
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to sphere
if sphere.data.materials:
    sphere.data.materials[0] = mat
else:
    sphere.data.materials.append(mat)

# Add world environment for better visualization
world = bpy.data.worlds.get("World")
if world:
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.8, 0.9, 1.0, 1.0)  # Light blue
        bg.inputs['Strength'].default_value = 1.0

# Add a ground plane for reference
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -4))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print(f"Created active sphere at {sphere.location}")
print(f"Radius: {sphere.dimensions.x / 2}")
print(f"Rotation (Z): {math.degrees(sphere.rotation_euler.z)}°")