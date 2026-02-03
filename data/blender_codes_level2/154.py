import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
tower_height = 12.0
base_size = 4.0
column_cross_section = 0.5
column_height = 12.0
beam_length = 4.0
beam_width = 0.5
beam_depth = 0.5
beam_levels = [3.0, 6.0, 9.0]
platform_size = 2.0
platform_thickness = 0.5
load_mass_kg = 2000.0
load_force_newton = 19620.0
ground_size = 20.0
ground_thickness = 1.0
column_positions = [(-2.0, -2.0, 0.0), (-2.0, 2.0, 0.0), (2.0, -2.0, 0.0), (2.0, 2.0, 0.0)]

# Create ground (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -ground_thickness/2))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (ground_size, ground_size, ground_thickness)
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create columns (active rigid bodies)
columns = []
for i, pos in enumerate(column_positions):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pos[0], pos[1], column_height/2))
    col = bpy.context.active_object
    col.name = f"Column_{i}"
    col.scale = (column_cross_section, column_cross_section, column_height)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.mass = 100.0  # Approximate steel mass (density adjusted)
    columns.append(col)

# Create beams at each level
beams = []
beam_directions = ['x', 'y']
for level in beam_levels:
    beam_center_z = level + beam_depth/2
    # X-direction beams (span along X, fixed Y = ±2)
    for y_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_sign*base_size/2, beam_center_z))
        beam = bpy.context.active_object
        beam.name = f"Beam_X_{level}_Y{y_sign}"
        beam.scale = (beam_length, beam_width, beam_depth)
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.mass = 50.0
        beams.append(beam)
    # Y-direction beams (span along Y, fixed X = ±2)
    for x_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_sign*base_size/2, 0.0, beam_center_z))
        beam = bpy.context.active_object
        beam.name = f"Beam_Y_{level}_X{x_sign}"
        beam.scale = (beam_width, beam_length, beam_depth)
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.mass = 50.0
        beams.append(beam)

# Create top platform
platform_center_z = tower_height + platform_thickness/2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, platform_center_z))
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (platform_size, platform_size, platform_thickness)
bpy.ops.rigidbody.object_add()
platform.rigid_body.mass = 200.0  # Platform self-mass

# Apply fixed constraints between column bases and ground
for col in columns:
    bpy.ops.object.select_all(action='DESELECT')
    ground.select_set(True)
    col.select_set(True)
    bpy.context.view_layer.objects.active = col
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{col.name}_to_Ground"

# Apply fixed constraints between columns and beams at intersections
for beam in beams:
    beam_loc = beam.location
    # Determine which columns this beam connects to based on beam name
    if 'Beam_X' in beam.name:
        # Connects to columns at Y = ±2
        connected_cols = [col for col in columns if abs(col.location.y - beam_loc.y) < 0.1]
    elif 'Beam_Y' in beam.name:
        # Connects to columns at X = ±2
        connected_cols = [col for col in columns if abs(col.location.x - beam_loc.x) < 0.1]
    for col in connected_cols:
        bpy.ops.object.select_all(action='DESELECT')
        col.select_set(True)
        beam.select_set(True)
        bpy.context.view_layer.objects.active = beam
        bpy.ops.rigidbody.constraint_add(type='FIXED')
        constraint = bpy.context.active_object
        constraint.name = f"Fix_{col.name}_{beam.name}"

# Apply fixed constraints between column tops and platform
for col in columns:
    bpy.ops.object.select_all(action='DESELECT')
    col.select_set(True)
    platform.select_set(True)
    bpy.context.view_layer.objects.active = platform
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{col.name}_to_Platform"

# Apply downward force at platform center (using rigid body force field)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, platform_center_z))
force_empty = bpy.context.active_object
force_empty.name = "Load_Force"
bpy.ops.object.forcefield_add(type='FORCE')
force_empty.field.strength = -load_force_newton  # Negative for downward
force_empty.field.use_gravity_falloff = False
force_empty.field.falloff_power = 0
force_empty.field.distance_max = 1.0  # Affect only nearby objects
# Parent force field to platform so it moves with it
force_empty.parent = platform

# Set rigid body world settings for simulation
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 250  # Simulate for 250 frames

print("Tower construction complete. Run simulation to verify stability.")