import bpy
import math

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define variables from parameter summary
col_dim = (0.2, 0.2, 12.0)
col_positions = [
    (-1.0, -1.0, 0.0), (-1.0, 1.0, 0.0),
    (1.0, -1.0, 0.0), (1.0, 1.0, 0.0),
    (-1.0, -1.0, 0.0), (-1.0, 1.0, 0.0),
    (1.0, -1.0, 0.0), (1.0, 1.0, 0.0)
]
beam_dim = (0.15, 0.15, 2.0)
brace_heights = [3.0, 6.0, 9.0, 12.0]
plat_dim = (2.0, 2.0, 0.1)
plat_heights = [4.0, 8.0, 12.0]
plat_ext = 1.5
plat_center_x = 1.75
load_dim = (0.5, 0.5, 0.5)
load_mass = 500.0
load_pos = (0.0, 1.5, 12.35)
sim_frames = 100

# 3. Create 8 vertical columns
columns = []
for i, pos in enumerate(col_positions):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
    col = bpy.context.active_object
    col.name = f"Column_{i}"
    col.scale = (col_dim[0]/2, col_dim[1]/2, col_dim[2]/2)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    columns.append(col)

# 4. Create cross-bracing beams at 4 levels
beams = []
for h in brace_heights:
    # Horizontal beams in X-direction (between columns with same Y)
    for y in [-1.0, 1.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y, h))
        beam = bpy.context.active_object
        beam.name = f"Beam_X_y{y}_z{h}"
        beam.scale = (beam_dim[2]/2, beam_dim[1]/2, beam_dim[0]/2)
        beam.rotation_euler = (0, math.pi/2, 0)
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        beams.append(beam)
    
    # Horizontal beams in Y-direction (between columns with same X)
    for x in [-1.0, 1.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.0, h))
        beam = bpy.context.active_object
        beam.name = f"Beam_Y_x{x}_z{h}"
        beam.scale = (beam_dim[0]/2, beam_dim[2]/2, beam_dim[1]/2)
        beam.rotation_euler = (math.pi/2, 0, 0)
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        beams.append(beam)

# 5. Create 3 cantilever platforms
platforms = []
for h in plat_heights:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, 
        location=(plat_center_x, 0.0, h + plat_dim[2]/2)
    )
    plat = bpy.context.active_object
    plat.name = f"Platform_z{h}"
    plat.scale = (plat_dim[0]/2, plat_dim[1]/2, plat_dim[2]/2)
    bpy.ops.rigidbody.object_add()
    plat.rigid_body.type = 'PASSIVE'
    platforms.append(plat)

# 6. Create load block on top platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos)
load = bpy.context.active_object
load.name = "Load_Block"
load.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.type = 'ACTIVE'

# 7. Create fixed constraints between structural elements
def add_fixed_constraint(obj1, obj2):
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj1.name}_{obj2.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2

# Connect platforms to nearest columns (X=+1 columns)
for plat in platforms:
    for col in columns:
        if abs(col.location.x - 1.0) < 0.1 and abs(col.location.y) < 1.1:
            add_fixed_constraint(plat, col)

# Connect beams to columns at each level
for beam in beams:
    beam_z = beam.location.z
    for col in columns:
        if abs(col.location.z + col_dim[2]/2 - beam_z) < 0.1:
            add_fixed_constraint(beam, col)

# 8. Setup physics simulation
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 9. Bake simulation (headless compatible)
print("Simulation setup complete. Run with: blender --background --python-expr 'import bpy; bpy.ops.ptcache.bake()'")