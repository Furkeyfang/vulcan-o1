import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
pillar_height = 12.0
pillar_width = 1.0
pillar_depth = 1.0
wall_thickness = 0.1
pillar_center_z = pillar_height / 2.0
load_mass_kg = 2000.0
load_size = (1.0, 1.0, 1.0)
load_center_z = pillar_height + load_size[2] / 2.0
ground_plane_size = 10.0

# Create hollow pillar using boolean difference
# Outer shell
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, pillar_center_z))
outer = bpy.context.active_object
outer.name = "Pillar_Outer"
outer.scale = (pillar_width, pillar_depth, pillar_height)

# Inner void (slightly taller to ensure clean cut)
inner_height = pillar_height + 0.001  # Avoid coplanar faces
inner_width = pillar_width - 2 * wall_thickness
inner_depth = pillar_depth - 2 * wall_thickness
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, pillar_center_z))
inner = bpy.context.active_object
inner.name = "Pillar_Inner"
inner.scale = (inner_width, inner_depth, inner_height)

# Boolean subtraction
outer.modifiers.new(name="Boolean", type='BOOLEAN')
outer.modifiers["Boolean"].operation = 'DIFFERENCE'
outer.modifiers["Boolean"].object = inner
bpy.context.view_layer.objects.active = outer
bpy.ops.object.modifier_apply(modifier="Boolean")

# Delete inner cube
bpy.ops.object.select_all(action='DESELECT')
inner.select_set(True)
bpy.ops.object.delete()

# Add physics to pillar
bpy.ops.rigidbody.object_add()
outer.rigid_body.type = 'PASSIVE'
outer.rigid_body.collision_shape = 'MESH'

# Create ground plane for visual reference (not strictly needed for physics)
bpy.ops.mesh.primitive_plane_add(size=ground_plane_size, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_center_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = load_size

# Add physics to load
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass_kg
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraint at base (pillar to world)
# In Blender, passive rigid body is already fixed to world, but we'll add explicit constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
constraint_base = bpy.context.active_object
constraint_base.name = "Fixed_Base"
bpy.ops.rigidbody.constraint_add()
constraint_base.rigid_body_constraint.type = 'FIXED'
constraint_base.rigid_body_constraint.object1 = outer

# Create fixed constraint at top (load to pillar)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, pillar_height))
constraint_top = bpy.context.active_object
constraint_top.name = "Fixed_Top"
bpy.ops.rigidbody.constraint_add()
constraint_top.rigid_body_constraint.type = 'FIXED'
constraint_top.rigid_body_constraint.object1 = load
constraint_top.rigid_body_constraint.object2 = outer

# Set world gravity (default is -9.8 Z, but explicit for clarity)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = mathutils.Vector((0.0, 0.0, -9.81))