import bpy
import math
import mathutils

# ========== PARAMETERS ==========
span = 8.0
bottom_z = 5.0
peak_z = 7.0
top_chord_length = 4.5
member_cross_section = 0.2

top_chord_horizontal = math.sqrt(top_chord_length**2 - (peak_z - bottom_z)**2)
vertical_center_height = 2.0
vertical_end_height = 0.5
vertical_mid_height = 1.25

nodes_bottom = [
    (-4.0, 0.0, 5.0),
    (-2.0, 0.0, 5.0),
    (0.0, 0.0, 5.0),
    (2.0, 0.0, 5.0),
    (4.0, 0.0, 5.0)
]

nodes_top = [
    (-top_chord_horizontal, 0.0, 5.0),
    (-2.0, 0.0, 6.25),
    (0.0, 0.0, 7.0),
    (2.0, 0.0, 6.25),
    (top_chord_horizontal, 0.0, 5.0)
]

# Member definitions as (start_node_idx, end_node_idx) using indices above
top_chords = [(0,1), (1,2), (2,3), (3,4)]
bottom_chords = [(0,1), (1,2), (2,3), (3,4)]
verticals = [(0,0), (1,1), (2,2), (3,3), (4,4)]
diagonals = [(0,1), (1,2), (2,3), (3,4)]

total_load_n = 5886.0
nodes_per_bottom = 5
force_per_node = total_load_n / nodes_per_bottom

frame_count = 100
collision_margin = 0.001
member_density = 500.0

# ========== SCENE SETUP ==========
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Set frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = frame_count

# ========== CREATE NODE EMPTIES ==========
node_empties = []  # Will store empty objects at node positions

for i, pos in enumerate(nodes_bottom + nodes_top):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
    empty = bpy.context.active_object
    empty.name = f"Node_{i}"
    
    # Add rigid body (passive - they won't move unless forced)
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.type = 'PASSIVE'
    empty.rigid_body.collision_margin = collision_margin
    
    node_empties.append(empty)

# ========== FUNCTION TO CREATE BEAM ==========
def create_beam(start_pos, end_pos, name):
    """Create a beam between two points with proper orientation"""
    # Calculate midpoint and direction
    start = mathutils.Vector(start_pos)
    end = mathutils.Vector(end_pos)
    midpoint = (start + end) / 2
    direction = end - start
    length = direction.length
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=midpoint)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: default cube is 2x2x2, so we need half dimensions
    beam.scale = (
        member_cross_section / 2,
        member_cross_section / 2,
        length / 2
    )
    
    # Rotate to align with direction
    if length > 0.0001:
        # Calculate rotation to align local Z axis with direction
        z_axis = mathutils.Vector((0, 0, 1))
        rotation = z_axis.rotation_difference(direction)
        beam.rotation_euler = rotation.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.collision_margin = collision_margin
    
    # Calculate and set mass (volume * density)
    volume = member_cross_section**2 * length
    mass = volume * member_density
    beam.rigid_body.mass = mass
    
    return beam

# ========== CREATE STRUCTURAL MEMBERS ==========
all_beams = []

# Top chords
for i, (idx1, idx2) in enumerate(top_chords):
    beam = create_beam(
        nodes_top[idx1],
        nodes_top[idx2],
        f"TopChord_{i}"
    )
    all_beams.append(beam)

# Bottom chords
for i, (idx1, idx2) in enumerate(bottom_chords):
    beam = create_beam(
        nodes_bottom[idx1],
        nodes_bottom[idx2],
        f"BottomChord_{i}"
    )
    all_beams.append(beam)

# Vertical members
for i, (bottom_idx, top_idx) in enumerate(verticals):
    beam = create_beam(
        nodes_bottom[bottom_idx],
        nodes_top[top_idx],
        f"Vertical_{i}"
    )
    all_beams.append(beam)

# Diagonal members
for i, (start_idx, end_idx) in enumerate(diagonals):
    # Use bottom node for start, top node for end
    beam = create_beam(
        nodes_bottom[start_idx],
        nodes_top[end_idx],
        f"Diagonal_{i}"
    )
    all_beams.append(beam)

# ========== CREATE FIXED CONSTRAINTS ==========
# Connect beams to node empties at their ends
for beam in all_beams:
    # Find which nodes this beam connects to
    beam_start = beam.location - beam.matrix_world @ mathutils.Vector((0, 0, beam.scale.z))
    beam_end = beam.location + beam.matrix_world @ mathutils.Vector((0, 0, beam.scale.z))
    
    # Find closest node empties
    start_node = min(node_empties, key=lambda n: (n.location - beam_start).length)
    end_node = min(node_empties, key=lambda n: (n.location - beam_end).length)
    
    # Create fixed constraint between beam and start node
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{beam.name}_start"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = beam
    constraint.rigid_body_constraint.object2 = start_node
    
    # Create fixed constraint between beam and end node
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Constraint_{beam.name}_end"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = beam
    constraint.rigid_body_constraint.object2 = end_node

# ========== APPLY LOADS ==========
# Apply downward force to bottom node empties (indices 0-4)
for i in range(5):
    node = node_empties[i]
    
    # Add force field (downward)
    bpy.ops.object.effector_add(type='FORCE', location=node.location)
    force = bpy.context.active_object
    force.name = f"Force_Node_{i}"
    force.field.strength = -force_per_node  # Negative for downward
    force.field.shape = 'POINT'
    force.field.falloff_power = 0
    
    # Parent force to node
    force.parent = node

# ========== FINAL SETUP ==========
# Set simulation quality
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Bake simulation (headless compatible)
bpy.context.scene.frame_set(1)
bpy.ops.ptcache.bake_all(bake=True)

print("Howe Truss construction complete. Simulation ready.")