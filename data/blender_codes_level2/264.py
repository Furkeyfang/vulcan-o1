import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
R_SIZE = 10.0
R_HEIGHT = 5.0
B_CROSS = 0.2
B_LENGTH = 10.0
GRID_SP = 1.0
N_GRID = 11
PLATE_THICK = 0.05
L_MASS = 2500.0
PLATE_OFFSET = 0.125
C_ITER = 50
C_ERROR = 0.1

# Function to create a beam with proper orientation
def create_beam(location, orientation, length, cross_section, name):
    """Create beam cube and scale to dimensions"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale based on orientation: 'X' or 'Y'
    if orientation == 'X':
        beam.scale = (length/2.0, cross_section/2.0, cross_section/2.0)
    else:  # 'Y' orientation
        beam.scale = (cross_section/2.0, length/2.0, cross_section/2.0)
    
    # Apply scale to mesh
    bpy.ops.object.transform_apply(scale=True)
    
    # Add rigid body physics (PASSIVE)
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE'
    beam.rigid_body.collision_shape = 'MESH'
    beam.rigid_body.collision_margin = 0.01
    
    return beam

# Create X-direction beams (Y fixed, X varies)
x_beams = {}
for i in range(N_GRID):
    y_pos = i * GRID_SP
    beam_name = f"Beam_X_{i}"
    beam_loc = (R_SIZE/2.0, y_pos, R_HEIGHT)  # Center along X
    beam = create_beam(beam_loc, 'X', B_LENGTH, B_CROSS, beam_name)
    x_beams[i] = beam

# Create Y-direction beams (X fixed, Y varies)
y_beams = {}
for j in range(N_GRID):
    x_pos = j * GRID_SP
    beam_name = f"Beam_Y_{j}"
    beam_loc = (x_pos, R_SIZE/2.0, R_HEIGHT)  # Center along Y
    beam = create_beam(beam_loc, 'Y', B_LENGTH, B_CROSS, beam_name)
    y_beams[j] = beam

# Create fixed constraints at all intersections
constraint_count = 0
for i in range(N_GRID):  # X-beam index (Y position)
    for j in range(N_GRID):  # Y-beam index (X position)
        # Create empty at intersection point for constraint pivot
        int_loc = (j * GRID_SP, i * GRID_SP, R_HEIGHT)
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=int_loc)
        empty = bpy.context.active_object
        empty.name = f"Constraint_Pivot_{i}_{j}"
        
        # Add rigid body constraint
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.name = f"Fixed_Constraint_{i}_{j}"
        constraint.empty_display_size = 0.2
        
        # Configure constraint properties
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = x_beams[i]
        constraint.rigid_body_constraint.object2 = y_beams[j]
        constraint.rigid_body_constraint.use_override_solver_iterations = True
        constraint.rigid_body_constraint.solver_iterations = C_ITER
        constraint.rigid_body_constraint.use_override_error = True
        constraint.rigid_body_constraint.error = C_ERROR
        
        # Parent empty to constraint for organization
        empty.parent = constraint
        
        constraint_count += 1

# Create load plate (distributed 2500kg mass)
plate_loc = (R_SIZE/2.0, R_SIZE/2.0, R_HEIGHT + B_CROSS/2.0 + PLATE_OFFSET)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plate_loc)
plate = bpy.context.active_object
plate.name = "Load_Plate"
plate.scale = (R_SIZE/2.0, R_SIZE/2.0, PLATE_THICK/2.0)
bpy.ops.object.transform_apply(scale=True)

# Add rigid body physics with mass
bpy.ops.rigidbody.object_add()
plate.rigid_body.type = 'ACTIVE'
plate.rigid_body.mass = L_MASS
plate.rigid_body.collision_shape = 'MESH'
plate.rigid_body.collision_margin = 0.01
plate.rigid_body.use_deactivation = False  # Keep active for continuous load

# Configure physics world settings
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
    
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0

print(f"Created {len(x_beams) + len(y_beams)} beams")
print(f"Created {constraint_count} fixed constraints")
print(f"Load plate mass: {L_MASS} kg")
print("Structure ready for load-bearing simulation")