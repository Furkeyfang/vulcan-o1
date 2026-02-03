import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
deck_len = 15.0
deck_wid = 3.0
deck_thick = 0.5
slope_deg = 5.0
col_rad = 0.5
col_base_h = 1.5
load_mass = 1000.0
load_size = 1.0

slope_rad = math.radians(slope_deg)
deck_dz = deck_len * math.sin(slope_rad)
right_col_h = col_base_h + deck_dz
deck_cx = 7.5 * math.cos(slope_rad) - 0.25 * math.sin(slope_rad)
deck_cz = 7.5 * math.sin(slope_rad) + 0.25 * math.cos(slope_rad)
left_col_cz = col_base_h / 2.0
right_col_x = deck_len * math.cos(slope_rad)
right_col_cz = right_col_h / 2.0
load_off_x = 0.25 * math.sin(slope_rad)
load_off_z = 0.25 * math.cos(slope_rad)
load_x = deck_cx + load_off_x
load_z = deck_cz + load_off_z

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create left column
bpy.ops.mesh.primitive_cylinder_add(radius=col_rad, depth=col_base_h, location=(0,0,left_col_cz))
left_col = bpy.context.active_object
left_col.name = "Left_Column"
left_col.rotation_euler = (math.pi/2, 0, 0)  # Rotate cylinder vertical (Blender default cylinder is Z-aligned)
bpy.ops.rigidbody.object_add()
left_col.rigid_body.type = 'PASSIVE'

# Create right column
bpy.ops.mesh.primitive_cylinder_add(radius=col_rad, depth=right_col_h, location=(right_col_x,0,right_col_cz))
right_col = bpy.context.active_object
right_col.name = "Right_Column"
right_col.rotation_euler = (math.pi/2, 0, 0)
bpy.ops.rigidbody.object_add()
right_col.rigid_body.type = 'PASSIVE'

# Create deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(deck_cx,0,deck_cz))
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = (deck_len, deck_wid, deck_thick)
deck.rotation_euler = (0, slope_rad, 0)
bpy.ops.rigidbody.object_add()
deck.rigid_body.type = 'ACTIVE'

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(load_x,0,load_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Add fixed constraints
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
empty = bpy.context.active_object
empty.name = "Constraints_Holder"

# Left column to deck
bpy.ops.object.constraint_add(type='FIXED')
constraint = bpy.context.active_object.constraints["Fixed"]
constraint.object1 = left_col
constraint.object2 = deck

# Right column to deck
bpy.ops.object.constraint_add(type='FIXED')
constraint = bpy.context.active_object.constraints["Fixed.001"]
constraint.object1 = right_col
constraint.object2 = deck

# Load to deck
bpy.ops.object.constraint_add(type='FIXED')
constraint = bpy.context.active_object.constraints["Fixed.002"]
constraint.object1 = load
constraint.object2 = deck

# Set simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Ensure proper collision shapes
for obj in [left_col, right_col, deck, load]:
    if obj.rigid_body:
        obj.rigid_body.collision_shape = 'MESH'