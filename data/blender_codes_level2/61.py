import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
bridge_length = 10.0
top_chord_z = 3.0
bottom_chord_z = 1.0
top_chord_cross = (0.2, 0.2)
bottom_chord_cross = (0.3, 0.3)
vertical_cross = (0.15, 0.15)
vertical_height = 2.0
vertical_positions = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
diagonal_cross = (0.15, 0.15)
load_mass = 900.0
load_size = (1.0, 1.0, 0.5)
load_position = (5.0, 0.0, 2.5)
material_density = 7850.0
support_size = (0.5, 2.0, 1.0)
support_positions = [(0.0, 0.0, 0.5), (10.0, 0.0, 0.5)]

# Create supports (ground connections)
for sup_pos in support_positions:
    bpy.ops.mesh.primitive_cube_add(size=1, location=sup_pos)
    sup = bpy.context.active_object
    sup.scale = support_size
    bpy.ops.rigidbody.object_add()
    sup.rigid_body.type = 'PASSIVE'
    sup.rigid_body.collision_shape = 'BOX'

# Create top chord
bpy.ops.mesh.primitive_cube_add(size=1, location=(bridge_length/2, 0, top_chord_z))
top_chord = bpy.context.active_object
top_chord.scale = (bridge_length, top_chord_cross[0], top_chord_cross[1])
bpy.ops.rigidbody.object_add()
top_chord.rigid_body.type = 'ACTIVE'
top_chord.rigid_body.collision_shape = 'BOX'
top_chord.rigid_body.mass = material_density * (bridge_length * top_chord_cross[0] * top_chord_cross[1])

# Create bottom chord
bpy.ops.mesh.primitive_cube_add(size=1, location=(bridge_length/2, 0, bottom_chord_z))
bottom_chord = bpy.context.active_object
bottom_chord.scale = (bridge_length, bottom_chord_cross[0], bottom_chord_cross[1])
bpy.ops.rigidbody.object_add()
bottom_chord.rigid_body.type = 'ACTIVE'
bottom_chord.rigid_body.collision_shape = 'BOX'
bottom_chord.rigid_body.mass = material_density * (bridge_length * bottom_chord_cross[0] * bottom_chord_cross[1])

# Create vertical members
vertical_members = []
for x in vertical_positions:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, (top_chord_z + bottom_chord_z)/2))
    vert = bpy.context.active_object
    vert.scale = (vertical_cross[0], vertical_cross[1], vertical_height)
    bpy.ops.rigidbody.object_add()
    vert.rigid_body.type = 'ACTIVE'
    vert.rigid_body.collision_shape = 'BOX'
    vert.rigid_body.mass = material_density * (vertical_cross[0] * vertical_cross[1] * vertical_height)
    vertical_members.append(vert)

# Create diagonal members
diagonal_members = []
for i in range(len(vertical_positions)-1):
    x1, x2 = vertical_positions[i], vertical_positions[i+1]
    
    # Alternate pattern
    if i % 2 == 0:  # From bottom-left to top-right
        start_z, end_z = bottom_chord_z, top_chord_z
    else:  # From top-left to bottom-right
        start_z, end_z = top_chord_z, bottom_chord_z
    
    # Calculate diagonal properties
    length = math.sqrt((x2 - x1)**2 + (end_z - start_z)**2)
    mid_x = (x1 + x2) / 2
    mid_z = (start_z + end_z) / 2
    angle = math.atan2(end_z - start_z, x2 - x1)
    
    # Create diagonal
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid_x, 0, mid_z))
    diag = bpy.context.active_object
    diag.scale = (length, diagonal_cross[0], diagonal_cross[1])
    diag.rotation_euler = (0, -angle, 0)  # Rotate around Y-axis
    bpy.ops.rigidbody.object_add()
    diag.rigid_body.type = 'ACTIVE'
    diag.rigid_body.collision_shape = 'BOX'
    diag.rigid_body.mass = material_density * (length * diagonal_cross[0] * diagonal_cross[1])
    diagonal_members.append(diag)

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=load_position)
load_cube = bpy.context.active_object
load_cube.scale = load_size
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.collision_shape = 'BOX'
load_cube.rigid_body.mass = load_mass

# Create fixed constraints at joints
all_members = [top_chord, bottom_chord] + vertical_members + diagonal_members

# Function to create constraint between two objects
def create_fixed_constraint(obj1, obj2, location):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.empty_display_size = 0.2
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    constraint.parent = empty

# Create constraints at each vertical joint
for x in vertical_positions:
    # Top joint (x, 0, top_chord_z)
    create_fixed_constraint(top_chord, next((v for v in vertical_members if v.location.x == x), None), (x, 0, top_chord_z))
    
    # Bottom joint (x, 0, bottom_chord_z)
    create_fixed_constraint(bottom_chord, next((v for v in vertical_members if v.location.x == x), None), (x, 0, bottom_chord_z))
    
    # Diagonal connections (connect to appropriate diagonals)
    for diag in diagonal_members:
        diag_x1 = diag.location.x - (diag.scale.x/2) * math.cos(diag.rotation_euler.y)
        diag_x2 = diag.location.x + (diag.scale.x/2) * math.cos(diag.rotation_euler.y)
        diag_z1 = diag.location.z - (diag.scale.x/2) * math.sin(diag.rotation_euler.y)
        diag_z2 = diag.location.z + (diag.scale.x/2) * math.sin(diag.rotation_euler.y)
        
        # Check if diagonal endpoint matches this joint
        if (abs(diag_x1 - x) < 0.01 and abs(diag_z1 - top_chord_z) < 0.01) or 
           (abs(diag_x1 - x) < 0.01 and abs(diag_z1 - bottom_chord_z) < 0.01) or 
           (abs(diag_x2 - x) < 0.01 and abs(diag_z2 - top_chord_z) < 0.01) or 
           (abs(diag_x2 - x) < 0.01 and abs(diag_z2 - bottom_chord_z) < 0.01):
            # Connect diagonal to top or bottom chord at this joint
            if abs(diag_z1 - top_chord_z) < 0.01 or abs(diag_z2 - top_chord_z) < 0.01:
                create_fixed_constraint(top_chord, diag, (x, 0, top_chord_z))
            else:
                create_fixed_constraint(bottom_chord, diag, (x, 0, bottom_chord_z))

# Connect load cube to top chord at center
create_fixed_constraint(top_chord, load_cube, (bridge_length/2, 0, top_chord_z))

# Setup simulation
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

print("Bridge construction complete. Simulation ready for 100 frames.")