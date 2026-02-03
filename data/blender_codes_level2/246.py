import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_length = 20.0
truss_spacing = 5.0
column_height = 5.0
column_size = (0.5, 0.5, 5.0)
beam_length = 12.0
beam_cross_section = (12.0, 0.5, 0.5)
central_joint_size = (1.0, 1.0, 1.0)
purlin_size = (0.3, 5.0, 0.3)
purlin_spacing = 4.0
num_purlins = 5
vertical_rise = math.sqrt(beam_length**2 - (span_length/2)**2)
apex_z = column_height + vertical_rise
vertical_shift = 5.0 - (apex_z + 0.0) / 2.0
total_load_kg = 2600.0
gravity = 9.81
total_force_N = total_load_kg * gravity
force_per_point = total_force_N / (2 + num_purlins)  # 2 central joints + purlins
left_column_x = -span_length/2
right_column_x = span_length/2
truss1_y = -truss_spacing/2
truss2_y = truss_spacing/2
apex_x = 0.0

# Helper function to create rigid body
def add_rigidbody(obj, type='ACTIVE', mass=10.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = type
    obj.rigid_body.mass = mass

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,-0.1))
ground = bpy.context.active_object
add_rigidbody(ground, 'PASSIVE')

# Function to create one truss assembly
def create_truss(truss_id, y_pos):
    suffix = f"_{truss_id}"
    
    # Columns (passive - fixed to ground)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(left_column_x, y_pos, column_height/2 + vertical_shift))
    col_left = bpy.context.active_object
    col_left.name = f"Column_L{suffix}"
    col_left.scale = column_size
    add_rigidbody(col_left, 'PASSIVE', 1000)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(right_column_x, y_pos, column_height/2 + vertical_shift))
    col_right = bpy.context.active_object
    col_right.name = f"Column_R{suffix}"
    col_right.scale = column_size
    add_rigidbody(col_right, 'PASSIVE', 1000)
    
    # Central joint
    bpy.ops.mesh.primitive_cube_add(size=1, location=(apex_x, y_pos, apex_z + vertical_shift))
    joint = bpy.context.active_object
    joint.name = f"Joint{suffix}"
    joint.scale = central_joint_size
    add_rigidbody(joint, 'ACTIVE', 200)
    
    # Diagonal beams (oriented using rotation)
    # Left beam: from left column to joint
    beam_left_loc = (
        (left_column_x + apex_x)/2,
        y_pos,
        (column_height + apex_z)/2 + vertical_shift
    )
    bpy.ops.mesh.primitive_cube_add(size=1, location=beam_left_loc)
    beam_left = bpy.context.active_object
    beam_left.name = f"Beam_L{suffix}"
    beam_left.scale = beam_cross_section
    # Rotate to align with diagonal
    angle = math.atan2(vertical_rise, span_length/2)
    beam_left.rotation_euler = (0, 0, -angle)
    add_rigidbody(beam_left, 'ACTIVE', 500)
    
    # Right beam
    beam_right_loc = (
        (right_column_x + apex_x)/2,
        y_pos,
        (column_height + apex_z)/2 + vertical_shift
    )
    bpy.ops.mesh.primitive_cube_add(size=1, location=beam_right_loc)
    beam_right = bpy.context.active_object
    beam_right.name = f"Beam_R{suffix}"
    beam_right.scale = beam_cross_section
    beam_right.rotation_euler = (0, 0, angle)
    add_rigidbody(beam_right, 'ACTIVE', 500)
    
    # Create fixed constraints
    def add_fixed_constraint(obj_a, obj_b):
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = obj_a
        constraint.rigid_body_constraint.object2 = obj_b
    
    # Column to beam connections
    add_fixed_constraint(col_left, beam_left)
    add_fixed_constraint(col_right, beam_right)
    # Beam to joint connections
    add_fixed_constraint(beam_left, joint)
    add_fixed_constraint(beam_right, joint)
    
    return col_left, col_right, beam_left, beam_right, joint

# Create both trusses
truss1_objs = create_truss("L1", truss1_y)
truss2_objs = create_truss("L2", truss2_y)

# Create purlins
purlins = []
purlin_x_positions = [(-span_length/2 + i*purlin_spacing) for i in range(num_purlins)]
for i, x in enumerate(purlin_x_positions):
    # Calculate Z position on diagonal (linear interpolation)
    x_frac = abs(x) / (span_length/2)
    z_pos = column_height + vertical_rise * (1 - x_frac) + vertical_shift
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z_pos))
    purlin = bpy.context.active_object
    purlin.name = f"Purlin_{i}"
    purlin.scale = purlin_size
    add_rigidbody(purlin, 'ACTIVE', 100)
    
    # Connect to both trusses' beams
    # Determine which beam to connect to based on x position
    for truss_objs in [truss1_objs, truss2_objs]:
        beam_left, beam_right = truss_objs[2], truss_objs[3]
        beam_to_connect = beam_left if x < 0 else beam_right
        
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.name = f"PurlinConstraint_{purlin.name}_{beam_to_connect.name}"
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = purlin
        constraint.rigid_body_constraint.object2 = beam_to_connect
    
    purlins.append(purlin)

# Apply forces to simulate load
# Apply to central joints and purlins
joints = [truss1_objs[4], truss2_objs[4]]
load_objects = joints + purlins

for obj in load_objects:
    if obj.rigid_body:
        # Apply downward force (negative Z)
        obj.rigid_body.use_gravity = True
        # Add constant force
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj.location)
        force_empty = bpy.context.active_object
        force_empty.name = f"Force_{obj.name}"
        force_empty.parent = obj
        # In headless mode, we can't use force fields directly without UI.
        # Alternative: Apply impulse over time or use Python to apply force each frame.
        # For this simulation, we'll rely on rigid body gravity and add mass to joints/purlins.
        obj.rigid_body.mass = force_per_point / gravity  # Mass equivalent to force

print(f"Structure built. Total load: {total_force_N}N, Force per point: {force_per_point}N")
print(f"Vertical shift applied: {vertical_shift}m to center at Z=5")