import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
total_span = 11.0
bridge_height = 1.5
beam_width = 0.2
beam_depth = 0.2
panel_lengths = [1.9186, 2.3023, 2.5581, 2.3023, 1.9186]
bottom_z = 0.0
top_z = bridge_height
load_mass = 700.0
load_force = load_mass * 9.81  # 6867 N
load_x = total_span / 2.0
load_z = bottom_z
support_base_w = 0.5
support_base_d = 0.5
support_base_h = 0.3

# Calculate cumulative X positions
cumulative_x = [0.0]
for pl in panel_lengths:
    cumulative_x.append(cumulative_x[-1] + pl)
# Ensure last point equals total_span (numerical precision)
cumulative_x[-1] = total_span

# Joint coordinates
bottom_joints = [(x, 0.0, bottom_z) for x in cumulative_x]
top_joints = [(x, 0.0, top_z) for x in cumulative_x]
num_joints = len(bottom_joints)

# Helper: create beam between two points
def create_beam(name, start, end, width, depth):
    # Calculate length and orientation
    vec = mathutils.Vector(end) - mathutils.Vector(start)
    length = vec.length
    center = (mathutils.Vector(start) + vec/2.0)
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (width, depth, length)
    
    # Rotate to align with vector
    if length > 0.001:
        # Default cube points along local Z
        up = mathutils.Vector((0,0,1))
        rot = up.rotation_difference(vec.normalized())
        beam.rotation_euler = rot.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = length * width * depth * 7850  # Steel density kg/m³
    return beam

# Helper: create fixed constraint between two objects
def create_fixed_constraint(name, obj_a, obj_b):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = name
    bpy.ops.rigidbody.constraint_add()
    con = empty.rigid_body_constraint
    con.type = 'FIXED'
    con.object1 = obj_a
    con.object2 = obj_b

# Create support bases at ends
for i, x in enumerate([0.0, total_span]):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x, 0.0, -support_base_h/2.0)
    )
    base = bpy.context.active_object
    base.name = f"Support_Base_{i}"
    base.scale = (support_base_w, support_base_d, support_base_h)
    bpy.ops.rigidbody.object_add()
    base.rigid_body.type = 'PASSIVE'

# Create bottom chord segments
bottom_beams = []
for i in range(num_joints-1):
    beam = create_beam(
        f"Bottom_Chord_{i}",
        bottom_joints[i],
        bottom_joints[i+1],
        beam_width,
        beam_depth
    )
    bottom_beams.append(beam)

# Create top chord segments
top_beams = []
for i in range(num_joints-1):
    beam = create_beam(
        f"Top_Chord_{i}",
        top_joints[i],
        top_joints[i+1],
        beam_width,
        beam_depth
    )
    top_beams.append(beam)

# Create vertical members
vertical_beams = []
for i in range(num_joints):
    beam = create_beam(
        f"Vertical_{i}",
        bottom_joints[i],
        top_joints[i],
        beam_width,
        beam_depth
    )
    vertical_beams.append(beam)

# Create diagonal members (Pratt pattern: from top left to bottom right, alternating)
diagonal_beams = []
for i in range(num_joints-1):
    if i % 2 == 0:  # Even: diagonal down-right
        beam = create_beam(
            f"Diagonal_{i}",
            top_joints[i],
            bottom_joints[i+1],
            beam_width,
            beam_depth
        )
    else:  # Odd: diagonal up-right (from bottom to top)
        beam = create_beam(
            f"Diagonal_{i}",
            bottom_joints[i],
            top_joints[i+1],
            beam_width,
            beam_depth
        )
    diagonal_beams.append(beam)

# Create fixed constraints at joints
# Bottom chord joints
for i in range(1, num_joints-1):
    left_beam = bottom_beams[i-1]
    right_beam = bottom_beams[i]
    vert_beam = vertical_beams[i]
    create_fixed_constraint(f"Bottom_Joint_{i}", left_beam, right_beam)
    create_fixed_constraint(f"Bottom_Vert_Joint_{i}", right_beam, vert_beam)

# Top chord joints
for i in range(1, num_joints-1):
    left_beam = top_beams[i-1]
    right_beam = top_beams[i]
    vert_beam = vertical_beams[i]
    create_fixed_constraint(f"Top_Joint_{i}", left_beam, right_beam)
    create_fixed_constraint(f"Top_Vert_Joint_{i}", right_beam, vert_beam)

# Diagonal connections (connect to appropriate chords)
for i, diag in enumerate(diagonal_beams):
    if i % 2 == 0:  # Connects top[i] to bottom[i+1]
        top_beam = top_beams[i]
        bottom_beam = bottom_beams[i+1]
        create_fixed_constraint(f"Diag_Top_{i}", diag, top_beam)
        create_fixed_constraint(f"Diag_Bottom_{i}", diag, bottom_beam)
    else:  # Connects bottom[i] to top[i+1]
        bottom_beam = bottom_beams[i]
        top_beam = top_beams[i+1]
        create_fixed_constraint(f"Diag_Bottom_{i}", diag, bottom_beam)
        create_fixed_constraint(f"Diag_Top_{i}", diag, top_beam)

# End supports: fix first and last vertical to support bases
create_fixed_constraint("Left_Support", vertical_beams[0], bpy.data.objects["Support_Base_0"])
create_fixed_constraint("Right_Support", vertical_beams[-1], bpy.data.objects["Support_Base_1"])

# Create load marker at center
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(load_x, 0.0, load_z))
load_marker = bpy.context.active_object
load_marker.name = "Load_Marker"
bpy.ops.rigidbody.object_add()
load_marker.rigid_body.type = 'ACTIVE'
load_marker.rigid_body.mass = 1.0  # Small mass

# Connect load marker to nearest bottom chord segment (between B2 and B3)
# Find segment containing load_x
seg_index = 0
for i in range(len(cumulative_x)-1):
    if cumulative_x[i] <= load_x <= cumulative_x[i+1]:
        seg_index = i
        break
nearest_beam = bottom_beams[seg_index]
create_fixed_constraint("Load_Connection", load_marker, nearest_beam)

# Apply force via force field (headless compatible)
bpy.ops.object.effector_add(type='FORCE', location=(load_x, 0.0, load_z))
force_field = bpy.context.active_object
force_field.name = "Load_Force"
force_field.field.strength = -load_force  # Negative for downward
force_field.field.direction = 'Z'  # Local Z axis
force_field.field.use_max_distance = True
force_field.field.distance_max = 0.15  # Only affect nearby objects
force_field.field.falloff_power = 0.0  # Constant within range

# Parent force field to load marker for easy positioning
force_field.parent = load_marker

# Set up simulation
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Pratt truss bridge created. Run simulation for 100 frames.")