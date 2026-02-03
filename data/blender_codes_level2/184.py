import bpy
import math
from mathutils import Matrix, Euler

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters from summary
base_side = 4.0
frame_height = 18.0
column_section = 0.5
beam_section = 0.5
diagonal_length = 5.65685424949
column_z_center = frame_height / 2.0
corner_x = base_side / 2.0
corner_y = base_side / 2.0
load_mass = 2200.0
load_size = 0.3
top_z = frame_height
mid_z = frame_height / 2.0
bottom_z = 0.0

# Helper to create cube with physics
def create_cube(name, location, scale, rigidbody_type='PASSIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigidbody_type
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Create four vertical columns
columns = []
for i, (x, y) in enumerate([(-corner_x, corner_y), (corner_x, corner_y),
                            (corner_x, -corner_y), (-corner_x, -corner_y)]):
    col = create_cube(f"Column_{i}", (x, y, column_z_center),
                      (column_section, column_section, frame_height))
    columns.append(col)

# Bottom horizontal beams (Z=0)
create_cube("Bottom_Beam_X1", (0.0, corner_y, bottom_z),
            (base_side, beam_section, beam_section))
create_cube("Bottom_Beam_X2", (0.0, -corner_y, bottom_z),
            (base_side, beam_section, beam_section))
create_cube("Bottom_Beam_Y1", (corner_x, 0.0, bottom_z),
            (beam_section, base_side, beam_section))
create_cube("Bottom_Beam_Y2", (-corner_x, 0.0, bottom_z),
            (beam_section, base_side, beam_section))

# Top horizontal beams (Z=18)
create_cube("Top_Beam_X1", (0.0, corner_y, top_z),
            (base_side, beam_section, beam_section))
create_cube("Top_Beam_X2", (0.0, -corner_y, top_z),
            (base_side, beam_section, beam_section))
create_cube("Top_Beam_Y1", (corner_x, 0.0, top_z),
            (beam_section, base_side, beam_section))
create_cube("Top_Beam_Y2", (-corner_x, 0.0, top_z),
            (beam_section, base_side, beam_section))

# Diagonal bracing beams at mid-height (Z=9)
# First diagonal: from (-2,2) to (2,-2) -> rotated -45° about Z
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, mid_z))
diag1 = bpy.context.active_object
diag1.name = "Diagonal_Beam_1"
diag1.scale = (diagonal_length, beam_section, beam_section)
diag1.rotation_euler = Euler((0.0, 0.0, -math.pi/4), 'XYZ')
bpy.ops.rigidbody.object_add()
diag1.rigid_body.type = 'PASSIVE'
diag1.rigid_body.collision_shape = 'BOX'

# Second diagonal: from (-2,-2) to (2,2) -> rotated +45° about Z
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, mid_z))
diag2 = bpy.context.active_object
diag2.name = "Diagonal_Beam_2"
diag2.scale = (diagonal_length, beam_section, beam_section)
diag2.rotation_euler = Euler((0.0, 0.0, math.pi/4), 'XYZ')
bpy.ops.rigidbody.object_add()
diag2.rigid_body.type = 'PASSIVE'
diag2.rigid_body.collision_shape = 'BOX'

# Create load mass (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, top_z))
load = bpy.context.active_object
load.name = "Load_Mass"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between all connecting elements
def add_fixed_constraint(obj1, obj2):
    # Select objects
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    const = bpy.context.active_object
    const.name = f"Fixed_{obj1.name}_{obj2.name}"
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj1
    const.rigid_body_constraint.object2 = obj2

# Connect each column to adjacent beams at its corner
beam_pairs = [
    ("Top_Beam_X1", "Top_Beam_Y1"), ("Top_Beam_X1", "Top_Beam_Y2"),
    ("Top_Beam_X2", "Top_Beam_Y1"), ("Top_Beam_X2", "Top_Beam_Y2"),
    ("Bottom_Beam_X1", "Bottom_Beam_Y1"), ("Bottom_Beam_X1", "Bottom_Beam_Y2"),
    ("Bottom_Beam_X2", "Bottom_Beam_Y1"), ("Bottom_Beam_X2", "Bottom_Beam_Y2")
]

# Manually create constraints between columns and beams at each corner
corner_connections = [
    # NW corner (-2,2)
    ("Column_0", "Top_Beam_X1"), ("Column_0", "Top_Beam_Y2"),
    ("Column_0", "Bottom_Beam_X1"), ("Column_0", "Bottom_Beam_Y2"),
    ("Column_0", "Diagonal_Beam_2"),
    # NE corner (2,2)
    ("Column_1", "Top_Beam_X1"), ("Column_1", "Top_Beam_Y1"),
    ("Column_1", "Bottom_Beam_X1"), ("Column_1", "Bottom_Beam_Y1"),
    ("Column_1", "Diagonal_Beam_1"),
    # SE corner (2,-2)
    ("Column_2", "Top_Beam_X2"), ("Column_2", "Top_Beam_Y1"),
    ("Column_2", "Bottom_Beam_X2"), ("Column_2", "Bottom_Beam_Y1"),
    ("Column_2", "Diagonal_Beam_2"),
    # SW corner (-2,-2)
    ("Column_3", "Top_Beam_X2"), ("Column_3", "Top_Beam_Y2"),
    ("Column_3", "Bottom_Beam_X2"), ("Column_3", "Bottom_Beam_Y2"),
    ("Column_3", "Diagonal_Beam_1")
]

# Also connect diagonals to opposite columns (already covered above)
# Connect load to top beams
top_beams = ["Top_Beam_X1", "Top_Beam_X2", "Top_Beam_Y1", "Top_Beam_Y2"]

# Apply all constraints
obj_dict = {obj.name: obj for obj in bpy.data.objects if obj.type == 'MESH'}
for obj1_name, obj2_name in corner_connections:
    if obj1_name in obj_dict and obj2_name in obj_dict:
        add_fixed_constraint(obj_dict[obj1_name], obj_dict[obj2_name])

for beam_name in top_beams:
    if beam_name in obj_dict:
        add_fixed_constraint(obj_dict[beam_name], load)

# Set up scene for simulation
scene = bpy.context.scene
scene.frame_end = 500
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 10
scene.rigidbody_world.use_split_impulse = True

print("Truss frame construction complete. Simulation ready.")