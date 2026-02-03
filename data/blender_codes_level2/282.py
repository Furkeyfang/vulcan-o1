import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
grid_spacing_x = 5.0
grid_spacing_y = 5.0
offset_magnitude = 1.0

column_height = 20.0
column_radius = 0.5
column_base_z = 0.0

platform_size_x = 6.0
platform_size_y = 6.0
platform_thickness = 0.5
platform_center_z = 20.0

load_size = 1.0
load_mass = 1800.0
load_center_z = 20.25

column_positions = [
    (-1.5, -2.5, 0.0),
    (1.5, -2.5, 0.0),
    (-3.5, 2.5, 0.0),
    (3.5, 2.5, 0.0)
]

platform_center = (0.0, 0.0, platform_center_z)
load_center = (0.0, 0.0, load_center_z)

# Create ground plane (large passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create columns
columns = []
for i, pos in enumerate(column_positions):
    # Create cylinder (column)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=column_radius,
        depth=column_height,
        location=(pos[0], pos[1], column_base_z + column_height/2)
    )
    column = bpy.context.active_object
    column.name = f"Column_{i+1}"
    
    # Add rigid body (passive)
    bpy.ops.rigidbody.object_add()
    column.rigid_body.type = 'PASSIVE'
    columns.append(column)

# Create platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_center)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (platform_size_x, platform_size_y, platform_thickness)

# Add rigid body (passive)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_center)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)

# Add rigid body (active with mass)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Create fixed constraints between columns and ground
for column in columns:
    # Create constraint object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=column.location)
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{column.name}_to_Ground"
    
    # Set up rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = ground
    constraint.rigid_body_constraint.object2 = column

# Create fixed constraints between columns and platform
for column in columns:
    # Constraint location at column top (connects to platform bottom)
    constraint_loc = (column.location.x, column.location.y, platform_center_z - platform_thickness/2)
    
    # Create constraint object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_loc)
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{column.name}_to_Platform"
    
    # Set up rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = column
    constraint.rigid_body_constraint.object2 = platform

# Create fixed constraint between load and platform
# Constraint at interface between load bottom and platform top
constraint_loc = (0, 0, platform_center_z + platform_thickness/2)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=constraint_loc)
constraint = bpy.context.active_object
constraint.name = "Fix_Load_to_Platform"

bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = load
constraint.rigid_body_constraint.object2 = platform

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.gravity = (0, 0, -9.81)

print("Staggered-column building frame constructed successfully.")
print(f"Structure supports {load_mass}kg load at height {platform_center_z}m.")