import bpy
import mathutils

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define variables from parameter summary
central_dim = (1.0, 1.0, 16.0)
central_loc = (0.0, 0.0, 8.0)
support_dim = (0.5, 0.5, 16.0)
support_locs = [
    (0.75, 0.75, 8.0),
    (0.75, -0.75, 8.0),
    (-0.75, 0.75, 8.0),
    (-0.75, -0.75, 8.0)
]
brace_dim = (2.0, 2.0, 0.2)
brace_z_levels = [4.0, 8.0, 12.0]
load_mass = 5500.0
load_dim = (1.0, 1.0, 0.5)
load_loc = (0.0, 0.0, 16.25)
ground_size = (10.0, 10.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)

# 3. Create ground plane (reference for constraints)
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.name = "Ground"

# 4. Create central column
bpy.ops.mesh.primitive_cube_add(size=1, location=central_loc)
central = bpy.context.active_object
central.scale = central_dim
bpy.ops.rigidbody.object_add()
central.rigid_body.type = 'PASSIVE'
central.name = "Central_Column"

# 5. Create four outer supports
supports = []
for idx, loc in enumerate(support_locs):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    sup = bpy.context.active_object
    sup.scale = support_dim
    bpy.ops.rigidbody.object_add()
    sup.rigid_body.type = 'PASSIVE'
    sup.name = f"Outer_Support_{idx+1}"
    supports.append(sup)

# 6. Create three horizontal braces
braces = []
for idx, z in enumerate(brace_z_levels):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,z))
    brace = bpy.context.active_object
    brace.scale = brace_dim
    bpy.ops.rigidbody.object_add()
    brace.rigid_body.type = 'PASSIVE'
    brace.name = f"Horizontal_Brace_{idx+1}"
    braces.append(brace)

# 7. Create load block
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.name = "Load_5500kg"

# 8. Add fixed constraints: vertical elements to ground
vertical_elements = [central] + supports
for elem in vertical_elements:
    bpy.ops.object.select_all(action='DESELECT')
    ground.select_set(True)
    elem.select_set(True)
    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.connect()

# 9. Add fixed constraints: each brace to all vertical elements
for brace in braces:
    for elem in vertical_elements:
        bpy.ops.object.select_all(action='DESELECT')
        elem.select_set(True)
        brace.select_set(True)
        bpy.context.view_layer.objects.active = elem
        bpy.ops.rigidbody.connect()

# 10. Set up scene physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -9.81)

# Optional: Set collision margin for stability
for obj in bpy.data.objects:
    if obj.rigid_body is not None:
        obj.rigid_body.collision_margin = 0.04

print("Reinforced box-frame pillar construction complete.")