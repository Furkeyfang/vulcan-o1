import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_size = 4.0
column_radius = 0.1
column_height = 3.0
beam_length = 4.0
beam_width = 0.1
beam_height = 0.1
platform_length = 4.0
platform_width = 4.0
platform_thickness = 0.2
num_levels = 3
total_height = 9.0
load_force = 1962.0
column_positions = [(-2.0, -2.0), (-2.0, 2.0), (2.0, -2.0), (2.0, 2.0)]
beam_y_positions = [-2.0, 2.0]
beam_x_positions = [-2.0, 2.0]
platform_z = 8.9

# Function to create fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.rigid_body.constraints[-1]
    constraint.type = 'FIXED'
    constraint.object2 = obj_b

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Store objects for later constraints
level_columns = [[] for _ in range(num_levels)]
level_beams = [[] for _ in range(num_levels)]

# Build each level
for level in range(num_levels):
    base_z = level * column_height
    # Create columns for this level
    for cx, cy in column_positions:
        col_z = base_z + column_height / 2
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=column_radius,
            depth=column_height,
            location=(cx, cy, col_z)
        )
        col = bpy.context.active_object
        col.name = f"Level_{level}_Column_{cx}_{cy}"
        bpy.ops.rigidbody.object_add()
        col.rigid_body.type = 'PASSIVE'
        col.rigid_body.collision_shape = 'CYLINDER'
        level_columns[level].append(col)
    
    # Create horizontal beams at bottom of level
    beam_z_bottom = base_z + beam_height / 2
    # X-direction beams (constant Y)
    for by in beam_y_positions:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, by, beam_z_bottom))
        beam = bpy.context.active_object
        beam.scale = (beam_length, beam_width, beam_height)
        beam.name = f"Level_{level}_XBeam_bottom_Y{by}"
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        level_beams[level].append(beam)
    
    # Y-direction beams (constant X)
    for bx in beam_x_positions:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 0, beam_z_bottom))
        beam = bpy.context.active_object
        beam.scale = (beam_width, beam_length, beam_height)
        beam.name = f"Level_{level}_YBeam_bottom_X{bx}"
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        level_beams[level].append(beam)
    
    # Create horizontal beams at top of level
    beam_z_top = base_z + column_height - beam_height / 2
    for by in beam_y_positions:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, by, beam_z_top))
        beam = bpy.context.active_object
        beam.scale = (beam_length, beam_width, beam_height)
        beam.name = f"Level_{level}_XBeam_top_Y{by}"
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        level_beams[level].append(beam)
    
    for bx in beam_x_positions:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 0, beam_z_top))
        beam = bpy.context.active_object
        beam.scale = (beam_width, beam_length, beam_height)
        beam.name = f"Level_{level}_YBeam_top_X{bx}"
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        level_beams[level].append(beam)

# Create fixed constraints within each level
for level in range(num_levels):
    # Connect each column to all beams in same level
    for col in level_columns[level]:
        for beam in level_beams[level]:
            add_fixed_constraint(col, beam)
    # Connect beams to each other (optional but thorough)
    for i, beam_a in enumerate(level_beams[level]):
        for beam_b in level_beams[level][i+1:]:
            if beam_a != beam_b:
                add_fixed_constraint(beam_a, beam_b)

# Connect columns vertically between levels
for level in range(num_levels - 1):
    for col_idx, col_lower in enumerate(level_columns[level]):
        col_upper = level_columns[level + 1][col_idx]
        add_fixed_constraint(col_lower, col_upper)

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, platform_z))
platform = bpy.context.active_object
platform.scale = (platform_length, platform_width, platform_thickness)
platform.name = "TopPlatform"
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = 200.0  # 200 kg

# Bond platform to top level beams
for beam in level_beams[num_levels - 1]:
    add_fixed_constraint(platform, beam)

# Apply constant downward force via force field
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, platform_z))
force_field = bpy.context.active_object
force_field.field.strength = -load_force  # Negative Z direction
force_field.field.use_global_coords = True
force_field.field.falloff_power = 0  # Uniform force
force_field.field.distance_max = 0.5  # Only affect nearby objects
# Link force field to platform
platform.field_settings.new(type='FORCE')
platform.field_settings[0].field = force_field.field

# Set up simulation parameters
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Ensure proper collision margins
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.04

print("Scaffolding tower construction complete. Run simulation for 100 frames.")