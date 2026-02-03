import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 9.0
height = 2.25
panel_width = 2.25
beam_w = 0.1
beam_h = 0.1
diag_len = 3.182
total_load = 8826.0
load_per_beam = 2206.5
steel_density = 7850.0
sim_frames = 100
max_deflection = 0.1

# Node coordinates (X, Y, Z)
bottom_nodes = [
    (0.0, 0.0, 0.0),
    (2.25, 0.0, 0.0),
    (4.5, 0.0, 0.0),
    (6.75, 0.0, 0.0),
    (9.0, 0.0, 0.0)
]
top_nodes = [
    (0.0, 0.0, height),
    (2.25, 0.0, height),
    (4.5, 0.0, height),
    (6.75, 0.0, height),
    (9.0, 0.0, height)
]

# Store beam objects for constraint creation
beam_objects = {}
constraint_empties = {}

def create_beam(name, start, end, scale_x):
    """Create rectangular beam between two points"""
    # Calculate midpoint and orientation
    start_v = Vector(start)
    end_v = Vector(end)
    mid = (start_v + end_v) * 0.5
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: X=length, Y=width, Z=height
    beam.scale = (scale_x * 0.5, beam_w * 0.5, beam_h * 0.5)
    
    # Rotate to align with direction vector
    direction = (end_v - start_v).normalized()
    if direction.length > 0:
        # Calculate rotation from X-axis to direction
        x_axis = Vector((1, 0, 0))
        angle = x_axis.angle(direction)
        axis = x_axis.cross(direction)
        if axis.length > 0:
            beam.rotation_mode = 'AXIS_ANGLE'
            beam.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = steel_density * (scale_x * beam_w * beam_h)
    beam.rigid_body.collision_shape = 'BOX'
    
    return beam

def create_joint_constraint(name, location, connected_beams):
    """Create empty at joint with fixed constraints to connected beams"""
    # Create empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Joint_{name}"
    
    # Make empty passive rigid body
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.type = 'PASSIVE'
    
    # Create fixed constraints between empty and each beam
    for beam in connected_beams:
        # Add constraint to empty
        bpy.context.view_layer.objects.active = empty
        bpy.ops.rigidbody.constraint_add()
        constraint = empty.rigid_body_constraint
        constraint.type = 'FIXED'
        constraint.object1 = empty
        constraint.object2 = beam
    
    return empty

# Create bottom chord beams
for i in range(4):
    name = f"Bottom_Chord_{i}"
    beam = create_beam(name, bottom_nodes[i], bottom_nodes[i+1], panel_width)
    beam_objects[name] = beam

# Create top chord beams
for i in range(4):
    name = f"Top_Chord_{i}"
    beam = create_beam(name, top_nodes[i], top_nodes[i+1], panel_width)
    beam_objects[name] = beam
    # Apply downward force to top chords
    beam.rigid_body.enabled = True
    # Force will be applied during animation

# Create vertical beams
vert_beams = []
for i in range(1, 4):  # Skip end verticals (Howe truss pattern)
    name = f"Vertical_{i}"
    beam = create_beam(name, bottom_nodes[i], top_nodes[i], height)
    beam_objects[name] = beam
    vert_beams.append(beam)

# Create diagonal beams
diag_beams = []
# Left diagonals (bottom to top)
for i in range(3):
    name = f"Diagonal_L_{i}"
    beam = create_beam(name, bottom_nodes[i], top_nodes[i+1], diag_len)
    beam_objects[name] = beam
    diag_beams.append(beam)

# Right diagonals (bottom to top, mirrored)
for i in range(1, 4):
    name = f"Diagonal_R_{i}"
    beam = create_beam(name, bottom_nodes[i], top_nodes[i-1], diag_len)
    beam_objects[name] = beam
    diag_beams.append(beam)

# Create fixed supports at ends (B0 and B4)
bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0, 0, -0.15))
support1 = bpy.context.active_object
support1.name = "Support_Left"
bpy.ops.rigidbody.object_add()
support1.rigid_body.type = 'PASSIVE'

bpy.ops.mesh.primitive_cube_add(size=0.3, location=(9.0, 0, -0.15))
support2 = bpy.context.active_object
support2.name = "Support_Right"
bpy.ops.rigidbody.object_add()
support2.rigid_body.type = 'PASSIVE'

# Create joint constraints
# Bottom joints
for i, node in enumerate(bottom_nodes):
    connected = []
    # Connect to adjacent bottom chords
    if i > 0:
        connected.append(beam_objects.get(f"Bottom_Chord_{i-1}"))
    if i < 4:
        connected.append(beam_objects.get(f"Bottom_Chord_{i}"))
    # Connect to vertical (if exists)
    if 1 <= i <= 3:
        connected.append(beam_objects.get(f"Vertical_{i}"))
    # Connect to diagonals
    if i < 3:
        connected.append(beam_objects.get(f"Diagonal_L_{i}"))
    if i > 0:
        connected.append(beam_objects.get(f"Diagonal_R_{i}"))
    
    # Filter out None values
    connected = [b for b in connected if b]
    
    if connected:
        create_joint_constraint(f"Bottom_{i}", node, connected)

# Top joints
for i, node in enumerate(top_nodes):
    connected = []
    # Connect to adjacent top chords
    if i > 0:
        connected.append(beam_objects.get(f"Top_Chord_{i-1}"))
    if i < 4:
        connected.append(beam_objects.get(f"Top_Chord_{i}"))
    # Connect to vertical (if exists)
    if 1 <= i <= 3:
        connected.append(beam_objects.get(f"Vertical_{i}"))
    # Connect to diagonals
    if i > 0:
        connected.append(beam_objects.get(f"Diagonal_L_{i-1}"))
    if i < 4:
        connected.append(beam_objects.get(f"Diagonal_R_{i}"))
    
    # Filter out None values
    connected = [b for b in connected if b]
    
    if connected:
        create_joint_constraint(f"Top_{i}", node, connected)

# Setup physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create animation for applying forces
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = sim_frames

# Apply forces to top chords using keyframes
for i in range(4):
    top_beam = beam_objects.get(f"Top_Chord_{i}")
    if top_beam:
        # Set initial force to 0
        top_beam.rigid_body.enabled = True
        top_beam.keyframe_insert(data_path="rigid_body.force", frame=1)
        
        # Apply downward force starting at frame 10
        top_beam.rigid_body.force = (0, 0, -load_per_beam)
        top_beam.keyframe_insert(data_path="rigid_body.force", frame=10)

# Set simulation end frame
bpy.context.scene.frame_set(sim_frames)

print("Howe Truss construction complete. Structure ready for simulation.")
print(f"Total load: {total_load}N applied as {load_per_beam}N per top chord beam")
print(f"Simulation will run for {sim_frames} frames")