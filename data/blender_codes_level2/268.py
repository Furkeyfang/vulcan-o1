import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
span_length = 25.0
tower_x_offset = 12.5
tower_dim = (2.0, 2.0, 10.0)
tower_left_loc = (-12.5, 0.0, 0.0)
tower_right_loc = (12.5, 0.0, 0.0)
deck_dim = (25.0, 4.0, 0.5)
deck_loc = (0.0, 0.0, 5.0)
deck_mass = 1200.0
cable_radius = 0.2
cable_length = 27.0
cable_y_left = -2.0
cable_y_right = 2.0
cable_z = 10.0
cable_left_loc = (0.0, -2.0, 10.0)
cable_right_loc = (0.0, 2.0, 10.0)
hanger_radius = 0.1
hanger_length = 5.0
hanger_x_positions = [-10.0, -5.0, 0.0, 5.0, 10.0]
hanger_y_left = -2.0
hanger_y_right = 2.0
hanger_z_top = 10.0
hanger_z_bottom = 5.0

# Enable rigid body physics
bpy.context.scene.use_gravity = True

# Helper function to add rigid body properties
def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'MESH'

# Helper function to add constraint between two objects
def add_constraint(obj1, obj2, location, constraint_type='FIXED', name="Constraint"):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint_obj = bpy.context.active_object
    constraint_obj.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_obj.rigid_body_constraint
    constraint.type = constraint_type
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    # For hinge constraints, set axis to Y (allowing rotation in XZ plane)
    if constraint_type == 'HINGE':
        constraint.use_limit_ang_z = True
        constraint.limit_ang_z_lower = -0.1  # Small allowance
        constraint.limit_ang_z_upper = 0.1

# Create left tower
bpy.ops.mesh.primitive_cube_add(size=1, location=tower_left_loc)
tower_left = bpy.context.active_object
tower_left.name = "Tower_Left"
tower_left.scale = tower_dim
add_rigidbody(tower_left, 'PASSIVE', 1000.0)  # Heavy passive mass

# Create right tower
bpy.ops.mesh.primitive_cube_add(size=1, location=tower_right_loc)
tower_right = bpy.context.active_object
tower_right.name = "Tower_Right"
tower_right.scale = tower_dim
add_rigidbody(tower_right, 'PASSIVE', 1000.0)

# Create deck
bpy.ops.mesh.primitive_cube_add(size=1, location=deck_loc)
deck = bpy.context.active_object
deck.name = "Deck"
deck.scale = deck_dim
add_rigidbody(deck, 'ACTIVE', deck_mass)

# Create left cable (aligned along X-axis)
bpy.ops.mesh.primitive_cylinder_add(
    radius=cable_radius, 
    depth=cable_length, 
    location=cable_left_loc
)
cable_left = bpy.context.active_object
cable_left.name = "Cable_Left"
cable_left.rotation_euler = (0, math.pi/2, 0)  # Rotate to align with X-axis
add_rigidbody(cable_left, 'ACTIVE', 100.0)

# Create right cable
bpy.ops.mesh.primitive_cylinder_add(
    radius=cable_radius, 
    depth=cable_length, 
    location=cable_right_loc
)
cable_right = bpy.context.active_object
cable_right.name = "Cable_Right"
cable_right.rotation_euler = (0, math.pi/2, 0)
add_rigidbody(cable_right, 'ACTIVE', 100.0)

# Create hanger bars (10 total: 5 on each side)
hangers = []
for i, x_pos in enumerate(hanger_x_positions):
    # Left side hangers (Y = -2)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=hanger_radius,
        depth=hanger_length,
        location=(x_pos, hanger_y_left, (hanger_z_top + hanger_z_bottom)/2)
    )
    hanger_left = bpy.context.active_object
    hanger_left.name = f"Hanger_Left_{i}"
    add_rigidbody(hanger_left, 'ACTIVE', 5.0)
    hangers.append(hanger_left)
    
    # Right side hangers (Y = 2)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=hanger_radius,
        depth=hanger_length,
        location=(x_pos, hanger_y_right, (hanger_z_top + hanger_z_bottom)/2)
    )
    hanger_right = bpy.context.active_object
    hanger_right.name = f"Hanger_Right_{i}"
    hanger_right.rotation_euler = (0, 0, 0)
    add_rigidbody(hanger_right, 'ACTIVE', 5.0)
    hangers.append(hanger_right)

# Add constraints
# 1. Tower to ground (fixed at base)
add_constraint(tower_left, None, tower_left_loc, 'FIXED', "TowerLeft_Ground")
add_constraint(tower_right, None, tower_right_loc, 'FIXED', "TowerRight_Ground")

# 2. Deck to towers (fixed at tower top connections)
deck_left_conn = (-tower_x_offset, 0.0, deck_loc[2])
deck_right_conn = (tower_x_offset, 0.0, deck_loc[2])
add_constraint(deck, tower_left, deck_left_conn, 'FIXED', "Deck_TowerLeft")
add_constraint(deck, tower_right, deck_right_conn, 'FIXED', "Deck_TowerRight")

# 3. Cables to towers (hinge at tower tops)
cable_left_conn_left = (-tower_x_offset, cable_y_left, cable_z)
cable_left_conn_right = (tower_x_offset, cable_y_left, cable_z)
cable_right_conn_left = (-tower_x_offset, cable_y_right, cable_z)
cable_right_conn_right = (tower_x_offset, cable_y_right, cable_z)

add_constraint(cable_left, tower_left, cable_left_conn_left, 'HINGE', "CableLeft_TowerLeft")
add_constraint(cable_left, tower_right, cable_left_conn_right, 'HINGE', "CableLeft_TowerRight")
add_constraint(cable_right, tower_left, cable_right_conn_left, 'HINGE', "CableRight_TowerLeft")
add_constraint(cable_right, tower_right, cable_right_conn_right, 'HINGE', "CableRight_TowerRight")

# 4. Hangers to cables and deck
for i, x_pos in enumerate(hanger_x_positions):
    # Left side connections
    hanger_top_left = (x_pos, hanger_y_left, hanger_z_top)
    hanger_bottom_left = (x_pos, hanger_y_left, hanger_z_bottom)
    
    hanger_left_obj = bpy.data.objects.get(f"Hanger_Left_{i}")
    if hanger_left_obj:
        add_constraint(hanger_left_obj, cable_left, hanger_top_left, 'FIXED', f"HangerLeft{i}_Cable")
        add_constraint(hanger_left_obj, deck, hanger_bottom_left, 'FIXED', f"HangerLeft{i}_Deck")
    
    # Right side connections
    hanger_top_right = (x_pos, hanger_y_right, hanger_z_top)
    hanger_bottom_right = (x_pos, hanger_y_right, hanger_z_bottom)
    
    hanger_right_obj = bpy.data.objects.get(f"Hanger_Right_{i}")
    if hanger_right_obj:
        add_constraint(hanger_right_obj, cable_right, hanger_top_right, 'FIXED', f"HangerRight{i}_Cable")
        add_constraint(hanger_right_obj, deck, hanger_bottom_right, 'FIXED', f"HangerRight{i}_Deck")

# Set simulation properties
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 250  # 250 frames at 60fps = ~4.17 seconds