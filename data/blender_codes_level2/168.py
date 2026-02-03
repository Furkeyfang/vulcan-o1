import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# ========== PARAMETERS FROM SUMMARY ==========
frame_height = 10.0
frame_width = 3.0
frame_depth = 2.0
element_cross_section = 0.2

column_size = (element_cross_section, element_cross_section, frame_height)
x_beam_size = (frame_width, element_cross_section, element_cross_section)
y_beam_size = (frame_depth, element_cross_section, element_cross_section)

column_x_positions = [frame_width/2, -frame_width/2, frame_width/2, -frame_width/2]
column_y_positions = [frame_depth/2, frame_depth/2, -frame_depth/2, -frame_depth/2]
column_z_center = frame_height/2

beam_z_levels = [
    element_cross_section/2,                    # Bottom level (on ground)
    2.5,                                        # First intermediate
    5.0,                                        # Second intermediate (mid-height)
    7.5,                                        # Third intermediate
    frame_height - element_cross_section/2      # Top level (below column top)
]

load_mass_kg = 3500.0
load_plate_size = (frame_width + 0.2, frame_depth + 0.2, 0.1)  # Slightly oversized
load_plate_z = frame_height + load_plate_size[2]/2
simulation_frames = 500

# ========== CREATE VERTICAL COLUMNS ==========
columns = []
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = column_size
    col.location = (column_x_positions[i], column_y_positions[i], column_z_center)
    columns.append(col)
    
    # Add rigid body physics (passive/static)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    col.rigid_body.collision_shape = 'BOX'

# ========== CREATE HORIZONTAL BEAMS (X-direction) ==========
x_beams = []
for z in beam_z_levels:
    # Front beam (positive Y)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    beam = bpy.context.active_object
    beam.name = f"X_Beam_front_Z{z}"
    beam.scale = x_beam_size
    beam.location = (0.0, frame_depth/2, z)
    x_beams.append(beam)
    
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'
    
    # Back beam (negative Y)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    beam = bpy.context.active_object
    beam.name = f"X_Beam_back_Z{z}"
    beam.scale = x_beam_size
    beam.location = (0.0, -frame_depth/2, z)
    x_beams.append(beam)
    
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'

# ========== CREATE HORIZONTAL BEAMS (Y-direction) ==========
y_beams = []
for z in beam_z_levels:
    # Right beam (positive X)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    beam = bpy.context.active_object
    beam.name = f"Y_Beam_right_Z{z}"
    beam.scale = y_beam_size
    beam.location = (frame_width/2, 0.0, z)
    y_beams.append(beam)
    
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'
    
    # Left beam (negative X)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    beam = bpy.context.active_object
    beam.name = f"Y_Beam_left_Z{z}"
    beam.scale = y_beam_size
    beam.location = (-frame_width/2, 0.0, z)
    y_beams.append(beam)
    
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'BOX'

# ========== CREATE FIXED CONSTRAINTS BETWEEN ALL CONNECTED PARTS ==========
# Collect all structural elements
all_elements = columns + x_beams + y_beams

# Create constraints between intersecting elements
# Strategy: For each column, connect to all beams at the same Z-level
for col in columns:
    col_x, col_y, col_z = col.location
    
    # Find beams at column height (within tolerance)
    for beam in x_beams + y_beams:
        beam_x, beam_y, beam_z = beam.location
        
        # Check if beam is at column height (same Z within cross-section tolerance)
        if abs(beam_z - col_z) < element_cross_section:
            # Check if beam intersects column in XY plane
            col_x_min = col_x - element_cross_section/2
            col_x_max = col_x + element_cross_section/2
            col_y_min = col_y - element_cross_section/2
            col_y_max = col_y + element_cross_section/2
            
            beam_x_min = beam_x - beam.scale.x/2
            beam_x_max = beam_x + beam.scale.x/2
            beam_y_min = beam_y - beam.scale.y/2
            beam_y_max = beam_y + beam.scale.y/2
            
            # Check for overlap
            x_overlap = (col_x_min < beam_x_max) and (col_x_max > beam_x_min)
            y_overlap = (col_y_min < beam_y_max) and (col_y_max > beam_y_min)
            
            if x_overlap and y_overlap:
                # Create fixed constraint
                bpy.ops.object.select_all(action='DESELECT')
                col.select_set(True)
                beam.select_set(True)
                bpy.context.view_layer.objects.active = col
                bpy.ops.rigidbody.constraint_add(type='FIXED')
                
                # Configure constraint
                constraint = bpy.context.active_object
                constraint.name = f"Fixed_{col.name}_{beam.name}"
                constraint.rigid_body_constraint.object1 = col
                constraint.rigid_body_constraint.object2 = beam
                constraint.rigid_body_constraint.disable_collisions = True

# ========== CREATE LOAD PLATE ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
load_plate = bpy.context.active_object
load_plate.name = "Load_Plate"
load_plate.scale = load_plate_size
load_plate.location = (0.0, 0.0, load_plate_z)

# Add rigid body physics with specified mass
bpy.ops.rigidbody.object_add()
load_plate.rigid_body.type = 'ACTIVE'
load_plate.rigid_body.mass = load_mass_kg
load_plate.rigid_body.collision_shape = 'BOX'
load_plate.rigid_body.use_margin = True
load_plate.rigid_body.collision_margin = 0.001

# ========== CONFIGURE PHYSICS WORLD ==========
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Set simulation duration
bpy.context.scene.frame_end = simulation_frames

# ========== VERIFICATION SETUP ==========
# Create a simple verification by recording initial and final positions
# In headless mode, we would typically run the simulation and check results
# This code sets up the scene; actual simulation would require bpy.ops.ptcache.bake()
print("Warehouse rack frame constructed successfully.")
print(f"Frame dimensions: {frame_width}m × {frame_depth}m × {frame_height}m")
print(f"Load: {load_mass_kg} kg plate positioned at Z={load_plate_z}m")
print(f"Simulation configured for {simulation_frames} frames")
print("To run simulation in headless mode, use: blender --background --python-expr 'bpy.ops.ptcache.bake()'")