import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_x = 4.0
base_y = 2.0
column_w = 0.5
column_d = 0.5
column_h_segment = 3.0
beam_w = 0.3
beam_h = 0.3
long_beam_l = 4.0
short_beam_l = 2.0
platform_h = 0.5
load_mass = 800.0
n_levels = 4
beam_levels = [3.15, 6.15, 9.15]
column_corners = [(-2.0, -1.0), (2.0, -1.0), (2.0, 1.0), (-2.0, 1.0)]
platform_loc = (0.0, 0.0, 12.25)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Store column segments for constraint creation
column_segments = []  # 4×4 list: [corner][level]

# Create columns for each corner
for corner_idx, (cx, cy) in enumerate(column_corners):
    corner_columns = []
    for level in range(n_levels):
        z_base = level * column_h_segment
        z_center = z_base + column_h_segment/2
        
        # Create column segment
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, z_center))
        col = bpy.context.active_object
        col.name = f"Column_{corner_idx}_{level}"
        col.scale = (column_w, column_d, column_h_segment)
        
        # Add rigid body (passive for structure)
        bpy.ops.rigidbody.object_add()
        col.rigid_body.type = 'PASSIVE'
        col.rigid_body.collision_shape = 'BOX'
        
        corner_columns.append(col)
        
        # Create fixed constraint between consecutive column segments
        if level > 0:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(cx, cy, z_base))
            empty = bpy.context.active_object
            empty.name = f"Constraint_{corner_idx}_{level-1}_{level}"
            
            bpy.ops.rigidbody.constraint_add()
            constraint = empty.rigid_body_constraint
            constraint.type = 'FIXED'
            constraint.object1 = corner_columns[level-1]
            constraint.object2 = col
    
    column_segments.append(corner_columns)

# Create beams at each level
for level_z in beam_levels:
    # Long beams (X-direction) at Y = ±1.0
    for y_pos in [-1.0, 1.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_pos, level_z))
        beam = bpy.context.active_object
        beam.name = f"LongBeam_Y{y_pos}_Z{level_z}"
        beam.scale = (long_beam_l, beam_w, beam_h)
        
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        beam.rigid_body.collision_shape = 'BOX'
        
        # Determine which columns this beam connects
        if y_pos == -1.0:
            col_indices = [0, 1]  # Columns A and B
        else:
            col_indices = [2, 3]  # Columns C and D
            
        # Create fixed constraints to columns
        for col_idx in col_indices:
            # Find column segment at this level (level = int(level_z/3) - 1)
            col_level = int(level_z / column_h_segment) - 1
            column = column_segments[col_idx][col_level]
            
            bpy.ops.object.empty_add(
                type='PLAIN_AXES', 
                location=(column_corners[col_idx][0], y_pos, level_z)
            )
            empty = bpy.context.active_object
            empty.name = f"BeamConstraint_{beam.name}_to_{column.name}"
            
            bpy.ops.rigidbody.constraint_add()
            constraint = empty.rigid_body_constraint
            constraint.type = 'FIXED'
            constraint.object1 = beam
            constraint.object2 = column
    
    # Short beams (Y-direction) at X = ±2.0
    for x_pos in [-2.0, 2.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0.0, level_z))
        beam = bpy.context.active_object
        beam.name = f"ShortBeam_X{x_pos}_Z{level_z}"
        beam.scale = (beam_w, short_beam_l, beam_h)
        
        bpy.ops.rigidbody.object_add()
        beam.rigid_body.type = 'PASSIVE'
        beam.rigid_body.collision_shape = 'BOX'
        
        # Determine which columns this beam connects
        if x_pos == -2.0:
            col_indices = [0, 3]  # Columns A and D
        else:
            col_indices = [1, 2]  # Columns B and C
            
        # Create fixed constraints to columns
        for col_idx in col_indices:
            col_level = int(level_z / column_h_segment) - 1
            column = column_segments[col_idx][col_level]
            
            bpy.ops.object.empty_add(
                type='PLAIN_AXES', 
                location=(x_pos, column_corners[col_idx][1], level_z)
            )
            empty = bpy.context.active_object
            empty.name = f"BeamConstraint_{beam.name}_to_{column.name}"
            
            bpy.ops.rigidbody.constraint_add()
            constraint = empty.rigid_body_constraint
            constraint.type = 'FIXED'
            constraint.object1 = beam
            constraint.object2 = column

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "TopPlatform"
platform.scale = (base_x, base_y, platform_h)

# Add rigid body with mass
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass
platform.rigid_body.collision_shape = 'BOX'

# Fix platform to top column segments
for corner_idx in range(4):
    top_column = column_segments[corner_idx][-1]  # Last segment (level 3)
    
    bpy.ops.object.empty_add(
        type='PLAIN_AXES',
        location=(column_corners[corner_idx][0], column_corners[corner_idx][1], 12.0)
    )
    empty = bpy.context.active_object
    empty.name = f"PlatformConstraint_to_Column{corner_idx}"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = platform
    constraint.object2 = top_column

# Configure simulation settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100

# Optional: Bake simulation for headless verification
# bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=100)