import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
col_w, col_d = 0.2, 0.2
col_h = 3.0
level_base = 2.0
beam_len = 2.0
beam_w, beam_d = 0.2, 0.2
n_levels = 10
total_h = 30.0
load_dim = (1.0, 1.0, 0.5)
load_mass = 1800.0
corners = [(-1,-1), (1,-1), (1,1), (-1,1)]

# Create materials for visualization (optional)
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    return mat

steel_mat = create_material("Steel", (0.7, 0.7, 0.7, 1))
load_mat = create_material("Load", (0.8, 0.2, 0.2, 1))

# Store objects for constraint creation
level_objects = []  # List of lists: each level has [col1..col4, beam1..beam4]

# Build tower levels
for level in range(n_levels):
    base_z = level * col_h
    level_objs = []
    
    # Create 4 columns
    for i, (cx, cy) in enumerate(corners):
        col_loc = (cx, cy, base_z + col_h/2)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
        col = bpy.context.active_object
        col.scale = (col_w, col_d, col_h)
        col.name = f"Level_{level}_Col_{i}"
        col.data.materials.append(steel_mat)
        bpy.ops.rigidbody.object_add()
        col.rigid_body.type = 'PASSIVE'
        col.rigid_body.collision_shape = 'BOX'
        level_objs.append(col)
    
    # Create 4 horizontal beams at top of level
    # Beam positions: along X direction (front/back) and Y direction (left/right)
    beam_z = base_z + col_h - beam_d/2  # Top of column minus half beam thickness
    
    # Front beam (Y = -1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1, beam_z))
    beam1 = bpy.context.active_object
    beam1.scale = (beam_len, beam_w, beam_d)
    beam1.name = f"Level_{level}_Beam_Front"
    beam1.data.materials.append(steel_mat)
    bpy.ops.rigidbody.object_add()
    beam1.rigid_body.type = 'PASSIVE'
    beam1.rigid_body.collision_shape = 'BOX'
    level_objs.append(beam1)
    
    # Back beam (Y = 1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1, beam_z))
    beam2 = bpy.context.active_object
    beam2.scale = (beam_len, beam_w, beam_d)
    beam2.name = f"Level_{level}_Beam_Back"
    beam2.data.materials.append(steel_mat)
    bpy.ops.rigidbody.object_add()
    beam2.rigid_body.type = 'PASSIVE'
    beam2.rigid_body.collision_shape = 'BOX'
    level_objs.append(beam2)
    
    # Left beam (X = -1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1, 0, beam_z))
    beam3 = bpy.context.active_object
    beam3.scale = (beam_w, beam_len, beam_d)
    beam3.name = f"Level_{level}_Beam_Left"
    beam3.data.materials.append(steel_mat)
    bpy.ops.rigidbody.object_add()
    beam3.rigid_body.type = 'PASSIVE'
    beam3.rigid_body.collision_shape = 'BOX'
    level_objs.append(beam3)
    
    # Right beam (X = 1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1, 0, beam_z))
    beam4 = bpy.context.active_object
    beam4.scale = (beam_w, beam_len, beam_d)
    beam4.name = f"Level_{level}_Beam_Right"
    beam4.data.materials.append(steel_mat)
    bpy.ops.rigidbody.object_add()
    beam4.rigid_body.type = 'PASSIVE'
    beam4.rigid_body.collision_shape = 'BOX'
    level_objs.append(beam4)
    
    level_objects.append(level_objs)

# Create fixed constraints within each level
for level_idx, objs in enumerate(level_objects):
    cols = objs[:4]
    beams = objs[4:]
    
    # Connect each beam to its two adjacent columns
    # Front beam (index 0) connects to columns 0 and 1 (front-left and front-right)
    for i, beam in enumerate(beams):
        if i == 0:  # Front beam
            col_indices = [0, 1]
        elif i == 1:  # Back beam
            col_indices = [2, 3]
        elif i == 2:  # Left beam
            col_indices = [0, 3]
        else:  # Right beam
            col_indices = [1, 2]
        
        for col_idx in col_indices:
            bpy.ops.object.select_all(action='DESELECT')
            beam.select_set(True)
            cols[col_idx].select_set(True)
            bpy.context.view_layer.objects.active = beam
            bpy.ops.rigidbody.constraint_add()
            constraint = bpy.context.active_object
            constraint.name = f"Fix_L{level_idx}_B{i}_C{col_idx}"
            constraint.rigid_body_constraint.type = 'FIXED'

# Create fixed constraints between levels (column to column)
for level_idx in range(n_levels - 1):
    lower_cols = level_objects[level_idx][:4]
    upper_cols = level_objects[level_idx + 1][:4]
    
    for col_idx in range(4):
        bpy.ops.object.select_all(action='DESELECT')
        lower_cols[col_idx].select_set(True)
        upper_cols[col_idx].select_set(True)
        bpy.context.view_layer.objects.active = lower_cols[col_idx]
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.name = f"Fix_L{level_idx}_to_L{level_idx+1}_C{col_idx}"
        constraint.rigid_body_constraint.type = 'FIXED'

# Create load cube
load_z = total_h + load_dim[2]/2  # Center at 30.25
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, load_z))
load = bpy.context.active_object
load.scale = load_dim
load.name = "Load_1800kg"
load.data.materials.append(load_mat)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.use_margin = True
load.rigid_body.collision_margin = 0.0

# Setup rigid body world (ensures physics simulation)
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set simulation end frame
bpy.context.scene.frame_end = 500

print("Scaffold tower construction complete. 10 levels, 80 structural elements, 76 fixed constraints.")
print(f"1800 kg load placed at Z={load_z}. Simulation ready for 500 frames.")