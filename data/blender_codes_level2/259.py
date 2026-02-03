import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
L_beam = 18.0
beam_width = 0.3
beam_depth = 0.3
theta_deg = 30.0
theta_rad = math.radians(theta_deg)
Z_bottom = 6.0
half_len = L_beam / 2.0
cos_theta = math.cos(theta_rad)
sin_theta = math.sin(theta_rad)
tan_theta = math.tan(theta_rad)
Z_cross = Z_bottom + half_len * sin_theta
truss_y_locations = [-6.0, 6.0]
purlin_count = 5
purlin_X_start = -half_len * cos_theta
purlin_X_step = (2 * half_len * cos_theta) / (purlin_count - 1)
purlin_X_list = [purlin_X_start + i * purlin_X_step for i in range(purlin_count)]
purlin_length_y = 12.0
purlin_width_x = 0.2
purlin_depth_z = 0.2
column_radius = 0.25
column_height = 6.0
column_X_list = [-half_len * cos_theta, half_len * cos_theta]
column_Y_list = [-6.0, 6.0]
purlin_mass = 380.0
gravity = -9.81

# Set gravity for rigid body world
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, gravity)

# Function to add rigid body properties
def add_rigid_body(obj, body_type='ACTIVE', mass=1.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'BOX'

# Create trusses
truss_beams = []  # List to store beam objects for each truss
for truss_y in truss_y_locations:
    beams = []
    for angle in [theta_rad, -theta_rad]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        beam = bpy.context.active_object
        beam.scale = (half_len, beam_width/2, beam_depth/2)  # Scale to (9,0.15,0.15) -> size (18,0.3,0.3)
        beam.rotation_euler = (0, angle, 0)
        beam.location = (0, truss_y, Z_cross)
        beam.name = f"Beam_Y{truss_y}_Angle{angle}"
        add_rigid_body(beam, body_type='ACTIVE')
        beams.append(beam)
    truss_beams.append(beams)
    
    # Add fixed constraint between the two beams of the truss at the crossing point
    if len(beams) == 2:
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"Truss_Constraint_Y{truss_y}"
        constraint.rigid_body_constraint.object1 = beams[0]
        constraint.rigid_body_constraint.object2 = beams[1]
        constraint.location = (0, truss_y, Z_cross)

# Create purlins
purlins = []
for i, X_p in enumerate(purlin_X_list):
    Z_p = Z_cross + abs(tan_theta * X_p)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(X_p, 0, Z_p))
    purlin = bpy.context.active_object
    purlin.scale = (purlin_width_x/2, purlin_length_y/2, purlin_depth_z/2)
    purlin.name = f"Purlin_{i}"
    add_rigid_body(purlin, body_type='ACTIVE', mass=purlin_mass)
    purlins.append(purlin)
    
    # Attach purlin to both trusses
    for truss_idx, truss_y in enumerate(truss_y_locations):
        # Determine which beam is the top at this X_p
        if X_p >= 0:
            beam = truss_beams[truss_idx][0]  # Beam with +theta (index 0)
        else:
            beam = truss_beams[truss_idx][1]  # Beam with -theta (index 1)
        
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"Purlin{i}_Truss{truss_idx}_Constraint"
        constraint.rigid_body_constraint.object1 = purlin
        constraint.rigid_body_constraint.object2 = beam
        constraint.location = (X_p, truss_y, Z_p)

# Create columns
columns = []
for X_c in column_X_list:
    for Y_c in column_Y_list:
        bpy.ops.mesh.primitive_cylinder_add(radius=column_radius, depth=column_height, location=(X_c, Y_c, column_height/2))
        column = bpy.context.active_object
        column.name = f"Column_X{X_c}_Y{Y_c}"
        add_rigid_body(column, body_type='PASSIVE')
        columns.append(column)
        
        # Determine which truss beam to attach to at the bottom point (Z=Z_bottom)
        truss_y = Y_c
        if X_c >= 0:
            beam = truss_beams[truss_y_locations.index(truss_y)][1]  # Beam with -theta for bottom
        else:
            beam = truss_beams[truss_y_locations.index(truss_y)][0]  # Beam with +theta for bottom
        
        # Fixed constraint between column top and truss bottom point
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"Column_X{X_c}_Y{Y_c}_Constraint"
        constraint.rigid_body_constraint.object1 = column
        constraint.rigid_body_constraint.object2 = beam
        constraint.location = (X_c, truss_y, Z_bottom)

# Optional: Add a ground plane for visualization (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
add_rigid_body(ground, body_type='PASSIVE')