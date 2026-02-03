import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract variables from parameter summary
span = 6.5
tie_z = 3.0
tie_length = 6.5
tie_width = 0.2
tie_height = 0.2
rafter_angle = 30.0
rafter_length = 3.752
rafter_width = 0.15
rafter_height = 0.15
ridge_z = 4.876
kingpost_height = 1.5
kingpost_width = 0.1
kingpost_depth = 0.1
strut_length = 1.720
strut_width = 0.1
strut_height = 0.1
connector_radius = 0.05
connector_depth = 0.1
load_mass = 350.0
load_length = 6.5
load_width = 0.5
load_height = 0.1
load_z = 3.15

# Helper function to create cylinder connector
def create_connector(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=connector_radius,
        depth=connector_depth,
        location=location
    )
    connector = bpy.context.active_object
    connector.name = name
    bpy.ops.rigidbody.object_add()
    connector.rigid_body.type = 'PASSIVE'
    return connector

# Create tie beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, tie_z))
tie = bpy.context.active_object
tie.name = "TieBeam"
tie.scale = (tie_length, tie_width, tie_height)
bpy.ops.rigidbody.object_add()
tie.rigid_body.type = 'ACTIVE'

# Create rafters
rafter_angle_rad = math.radians(rafter_angle)
# Left rafter
bpy.ops.mesh.primitive_cube_add(size=1, location=(-span/2, 0, tie_z))
left_rafter = bpy.context.active_object
left_rafter.name = "LeftRafter"
left_rafter.scale = (rafter_length, rafter_width, rafter_height)
left_rafter.rotation_euler = (0, 0, -rafter_angle_rad)
bpy.ops.rigidbody.object_add()
# Right rafter
bpy.ops.mesh.primitive_cube_add(size=1, location=(span/2, 0, tie_z))
right_rafter = bpy.context.active_object
right_rafter.name = "RightRafter"
right_rafter.scale = (rafter_length, rafter_width, rafter_height)
right_rafter.rotation_euler = (0, 0, rafter_angle_rad)
bpy.ops.rigidbody.object_add()

# Create King Post
kingpost_z = ridge_z - kingpost_height/2
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, kingpost_z))
kingpost = bpy.context.active_object
kingpost.name = "KingPost"
kingpost.scale = (kingpost_width, kingpost_depth, kingpost_height)
bpy.ops.rigidbody.object_add()

# Create struts
strut_angle = math.atan((ridge_z - tie_z)/2 / (span/4))  # Angle from horizontal
# Left strut
bpy.ops.mesh.primitive_cube_add(size=1, location=(-span/4, 0, (tie_z + ridge_z)/2))
left_strut = bpy.context.active_object
left_strut.name = "LeftStrut"
left_strut.scale = (strut_length, strut_width, strut_height)
left_strut.rotation_euler = (0, 0, -strut_angle)
bpy.ops.rigidbody.object_add()
# Right strut
bpy.ops.mesh.primitive_cube_add(size=1, location=(span/4, 0, (tie_z + ridge_z)/2))
right_strut = bpy.context.active_object
right_strut.name = "RightStrut"
right_strut.scale = (strut_length, strut_width, strut_height)
right_strut.rotation_euler = (0, 0, strut_angle)
bpy.ops.rigidbody.object_add()

# Create cylindrical connectors at all joints
connectors = []
# Tie beam ends
connectors.append(create_connector("Connector_TieLeft", (-span/2, 0, tie_z)))
connectors.append(create_connector("Connector_TieRight", (span/2, 0, tie_z)))
# Ridge point
connectors.append(create_connector("Connector_Ridge", (0, 0, ridge_z)))
# King post base (tie beam center)
connectors.append(create_connector("Connector_Center", (0, 0, tie_z)))
# Strut connections on rafters (midpoints)
connectors.append(create_connector("Connector_StrutLeft", (-span/4, 0, (tie_z + ridge_z)/2)))
connectors.append(create_connector("Connector_StrutRight", (span/4, 0, (tie_z + ridge_z)/2)))
# King post to strut connection (base)
connectors.append(create_connector("Connector_KingBase", (0, 0, ridge_z - kingpost_height)))

# Create load block
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, load_z))
load = bpy.context.active_object
load.name = "LoadBlock"
load.scale = (load_length, load_width, load_height)
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create fixed constraints between beams and connectors
def add_fixed_constraint(obj1, obj2):
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    constraint = obj1.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object2 = obj2

# Connect tie beam to end connectors
add_fixed_constraint(tie, connectors[0])
add_fixed_constraint(tie, connectors[1])

# Connect rafters to connectors (each rafter connects to tie end and ridge)
add_fixed_constraint(left_rafter, connectors[0])  # Left end
add_fixed_constraint(left_rafter, connectors[2])  # Ridge
add_fixed_constraint(right_rafter, connectors[1])  # Right end
add_fixed_constraint(right_rafter, connectors[2])  # Ridge

# Connect King Post
add_fixed_constraint(kingpost, connectors[2])  # Ridge
add_fixed_constraint(kingpost, connectors[3])  # Center

# Connect struts
add_fixed_constraint(left_strut, connectors[4])  # Left strut midpoint
add_fixed_constraint(left_strut, connectors[6])  # King base
add_fixed_constraint(right_strut, connectors[5])  # Right strut midpoint
add_fixed_constraint(right_strut, connectors[6])  # King base

# Frame settings for simulation
bpy.context.scene.frame_end = 100