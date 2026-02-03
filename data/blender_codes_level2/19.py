import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span_length = 7.0
truss_height = 1.01
truss_depth = 0.5
triangle_side = span_length / 6.0  # 1.1666667
num_triangles = 6
num_joints = num_triangles + 1
joint_x_start = -span_length / 2.0  # -3.5
cube_cross_section = 0.1
member_depth = truss_depth
support_width = 0.2
support_height = truss_height
load_mass = 600.0
load_size = 0.3
simulation_frames = 100

# Precompute joint positions
top_joints = []
bottom_joints = []
for i in range(num_joints):
    x = joint_x_start + i * triangle_side
    top_joints.append((x, 0.0, truss_height))
    bottom_joints.append((x, 0.0, 0.0))

# Helper to create a beam between two points
def create_beam(p1, p2, name, depth):
    # Calculate midpoint, length, and direction
    mid = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2, (p1[2] + p2[2])/2)
    length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)**0.5
    direction = mathutils.Vector(p2) - mathutils.Vector(p1)
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    # Scale: length in X, cross-section in Y/Z
    beam.scale = (length/2.0, cube_cross_section/2.0, depth/2.0)
    # Rotate to align X-axis with direction
    rot_quat = direction.to_track_quat('X', 'Z')
    beam.rotation_euler = rot_quat.to_euler()
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.collision_shape = 'BOX'
    return beam

# Create top chord beams
top_beams = []
for i in range(num_triangles):
    beam = create_beam(top_joints[i], top_joints[i+1], f"Top_Chord_{i}", member_depth)
    top_beams.append(beam)

# Create bottom chord beams
bottom_beams = []
for i in range(num_triangles):
    beam = create_beam(bottom_joints[i], bottom_joints[i+1], f"Bottom_Chord_{i}", member_depth)
    bottom_beams.append(beam)

# Create diagonal braces (alternating)
diagonals = []
for i in range(num_triangles):
    # Diagonal from bottom joint i to top joint i+1
    diag1 = create_beam(bottom_joints[i], top_joints[i+1], f"Diagonal_BottomToTop_{i}", member_depth)
    diagonals.append(diag1)
    # Diagonal from top joint i to bottom joint i+1
    diag2 = create_beam(top_joints[i], bottom_joints[i+1], f"Diagonal_TopToBottom_{i}", member_depth)
    diagonals.append(diag2)

# Create supports (passive rigid bodies)
# Left support
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(joint_x_start, 0.0, support_height/2))
support_left = bpy.context.active_object
support_left.name = "Support_Left"
support_left.scale = (support_width/2.0, support_width/2.0, support_height/2.0)
bpy.ops.rigidbody.object_add()
support_left.rigid_body.type = 'PASSIVE'
support_left.rigid_body.collision_shape = 'BOX'

# Right support
right_x = joint_x_start + span_length
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(right_x, 0.0, support_height/2))
support_right = bpy.context.active_object
support_right.name = "Support_Right"
support_right.scale = (support_width/2.0, support_width/2.0, support_height/2.0)
bpy.ops.rigidbody.object_add()
support_right.rigid_body.type = 'PASSIVE'
support_right.rigid_body.collision_shape = 'BOX'

# Create central load
center_top = top_joints[num_triangles//2]  # middle joint
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_top[0], 0.0, center_top[2] + load_size/2))
load = bpy.context.active_object
load.name = "Central_Load"
load.scale = (load_size/2.0, load_size/2.0, load_size/2.0)
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Add fixed constraints between members at joints
# We'll connect beams that share a joint using empty objects as parents
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    # Parent both objects to empty (simulates rigid connection via fixed constraint)
    obj_a.parent = empty
    obj_b.parent = empty
    # Keep transformations
    obj_a.matrix_parent_inverse = empty.matrix_world.inverted()
    obj_b.matrix_parent_inverse = empty.matrix_world.inverted()
    # Add rigid body constraint to empty (optional, parenting is sufficient for rigidity in simulation)
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'

# Connect top chord beams at joints
for i in range(num_triangles-1):
    add_fixed_constraint(top_beams[i], top_beams[i+1])

# Connect bottom chord beams at joints
for i in range(num_triangles-1):
    add_fixed_constraint(bottom_beams[i], bottom_beams[i+1])

# Connect diagonals to chords at joints (simplified: connect first diagonal to adjacent chord)
# In practice, you'd connect all beams meeting at a joint; here we connect representative pairs
for i in range(num_triangles):
    # Connect diagonal (bottom->top) to bottom chord at joint i
    diag_idx = 2*i
    if i < len(bottom_beams):
        add_fixed_constraint(diagonals[diag_idx], bottom_beams[i])
    # Connect diagonal (top->bottom) to top chord at joint i
    if i < len(top_beams):
        add_fixed_constraint(diagonals[diag_idx+1], top_beams[i])

# Connect load to top chord center beam
center_beam_idx = num_triangles // 2
add_fixed_constraint(load, top_beams[center_beam_idx])

# Setup physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = simulation_frames

# Keyframe rigid body states at frame 1
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.keyframe_insert(data_path="rigid_body.kinematic", frame=1)

# Run simulation (in headless, this will be computed when rendering or baking)
bpy.ops.ptcache.bake_all(bake=True)

print("Warren Truss platform with 600 kg load created. Simulation baked for 100 frames.")