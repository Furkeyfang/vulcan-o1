import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
total_length = 4.0
num_bays = 6
bay_length = total_length / num_bays
bottom_z = 2.5
truss_depth = 0.5
top_z = bottom_z + truss_depth
cross_section = 0.1
wall_thickness = 0.2
wall_height_min = 2.0
wall_height_max = 4.0
force_total = 3924.0
force_per_node = force_total / num_bays  # 6 nodes T1-T6
diagonal_length = math.sqrt(bay_length**2 + truss_depth**2)

# Helper: Create a beam between two points
def create_beam(start, end, name):
    # Calculate midpoint and direction
    mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2)
    direction = mathutils.Vector(end) - mathutils.Vector(start)
    length = direction.length
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = (cross_section / 2, cross_section / 2, length / 2)  # Cube size=1, so half-dimensions
    
    # Rotate to align with direction
    beam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    
    # Add rigid body (active by default)
    bpy.ops.rigidbody.object_add()
    return beam

# 1. Create support wall (passive rigid body)
wall_center_x = -wall_thickness / 2
wall_center_z = (wall_height_min + wall_height_max) / 2
wall_height = wall_height_max - wall_height_min
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wall_center_x, 0.0, wall_center_z))
wall = bpy.context.active_object
wall.scale = (wall_thickness / 2, 2.0, wall_height / 2)  # 2m wide in Y
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'

# 2. Generate node coordinates
bottom_nodes = [(i * bay_length, 0.0, bottom_z) for i in range(num_bays + 1)]
top_nodes = [(i * bay_length, 0.0, top_z) for i in range(num_bays + 1)]

# 3. Create truss members
members = []
# Bottom chord (tension)
for i in range(num_bays):
    beam = create_beam(bottom_nodes[i], bottom_nodes[i+1], f"BottomChord_{i}")
    members.append(beam)
# Top chord (compression)
for i in range(num_bays):
    beam = create_beam(top_nodes[i], top_nodes[i+1], f"TopChord_{i}")
    members.append(beam)
# Verticals (compression)
for i in range(num_bays + 1):
    beam = create_beam(bottom_nodes[i], top_nodes[i], f"Vertical_{i}")
    members.append(beam)
# Diagonals (tension) - Pratt orientation: top i to bottom i+1
for i in range(num_bays):
    beam = create_beam(top_nodes[i], bottom_nodes[i+1], f"Diagonal_{i}")
    members.append(beam)

# 4. Create fixed constraints at nodes
# First, create empty objects at each node to act as constraint anchors
node_empties = {}
for i, pos in enumerate(bottom_nodes + top_nodes):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
    empty = bpy.context.active_object
    empty.name = f"Node_{'B' if i <= num_bays else 'T'}{i if i <= num_bays else i - num_bays - 1}"
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.type = 'PASSIVE'
    node_empties[tuple(pos)] = empty

# Connect wall to supported nodes (B0 and T0)
for pos in [bottom_nodes[0], top_nodes[0]]:
    constraint = wall.constraints.new(type='RIGID_BODY_JOINT')
    constraint.object1 = wall
    constraint.object2 = node_empties[tuple(pos)]
    constraint.type = 'FIXED'

# Connect each member to its two node empties
for beam in members:
    # Find which nodes this beam connects to (simplified: check distance)
    for node_pos, empty in node_empties.items():
        dist1 = (mathutils.Vector(beam.location) - mathutils.Vector(node_pos)).length
        if dist1 < 0.01:  # Tolerance
            constraint = beam.constraints.new(type='RIGID_BODY_JOINT')
            constraint.object1 = beam
            constraint.object2 = empty
            constraint.type = 'FIXED'

# 5. Apply downward forces to top chord nodes T1-T6
for i in range(1, num_bays + 1):  # T1 to T6
    empty = node_empties[top_nodes[i]]
    # Create force field at node location
    bpy.ops.object.effector_add(type='FORCE', location=top_nodes[i])
    force = bpy.context.active_object
    force.name = f"Force_T{i}"
    force.field.strength = -force_per_node  # Negative for downward
    force.field.direction = (0.0, 0.0, -1.0)
    force.field.falloff_power = 0
    # Limit force to affect only this empty
    force.field.affected_collection = None
    force.field.use_max_distance = True
    force.field.distance_max = 0.1
    # Parent force to empty so it moves with node
    force.parent = empty

# 6. Set up rigid world for simulation
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Pratt truss overhang construction complete.")