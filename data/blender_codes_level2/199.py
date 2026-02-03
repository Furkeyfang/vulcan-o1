import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
span = 10.0
pitch_deg = 30.0
pitch_rad = math.radians(pitch_deg)
total_load_kg = 800.0
gravity = 9.8
top_chord_cs = 0.2
bottom_chord_cs = 0.2
web_cs = 0.15
member_depth = 0.3
apex_height = (span/2) * math.tan(pitch_rad)
half_span = span/2
top_chord_length = half_span / math.cos(pitch_rad)
panel_length = span/4
web_node_height = apex_height * 0.5
load_per_node_kg = total_load_kg/5
force_per_node = load_per_node_kg * gravity
steel_density = 7850.0

# Node coordinates (X, Z, Y=0)
nodes = {
    'A': (-half_span, 0.0, 0.0),          # Left support
    'B': (-panel_length, 0.0, 0.0),       # Left bottom panel point
    'C': (0.0, 0.0, 0.0),                 # Center bottom
    'D': (panel_length, 0.0, 0.0),        # Right bottom panel point
    'E': (half_span, 0.0, 0.0),           # Right support
    'F': (-half_span, apex_height, 0.0),  # Left top start (same as A but elevated for top chord)
    'G': (-panel_length, web_node_height, 0.0),  # Left top web connection
    'H': (0.0, apex_height, 0.0),         # Apex
    'I': (panel_length, web_node_height, 0.0),   # Right top web connection
    'J': (half_span, apex_height, 0.0)    # Right top end
}

# Member definitions: (start_node, end_node, cross_section, is_top_chord)
members = [
    ('A', 'B', bottom_chord_cs, False),   # Bottom chord left
    ('B', 'C', bottom_chord_cs, False),   # Bottom chord center left
    ('C', 'D', bottom_chord_cs, False),   # Bottom chord center right
    ('D', 'E', bottom_chord_cs, False),   # Bottom chord right
    ('F', 'G', top_chord_cs, True),       # Top chord left outer
    ('G', 'H', top_chord_cs, True),       # Top chord left inner
    ('H', 'I', top_chord_cs, True),       # Top chord right inner
    ('I', 'J', top_chord_cs, True),       # Top chord right outer
    ('B', 'G', web_cs, False),            # Left vertical web
    ('D', 'I', web_cs, False),            # Right vertical web
    ('C', 'G', web_cs, False),            # Left diagonal web
    ('C', 'I', web_cs, False),            # Right diagonal web
    ('C', 'H', web_cs, False)             # Center vertical
]

# Create member function
def create_member(name, start, end, cross_section):
    """Create a rectangular beam between two points"""
    start_vec = Vector(start)
    end_vec = Vector(end)
    direction = end_vec - start_vec
    length = direction.length
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: cross_section in X, member_depth in Y, length in Z
    beam.scale = (cross_section/2, member_depth/2, length/2)
    
    # Position at midpoint
    midpoint = (start_vec + end_vec) / 2
    beam.location = midpoint
    
    # Rotate to align with direction vector
    if length > 0.0001:
        up = Vector((0, 0, 1))
        rot_quat = direction.to_track_quat('Z', 'Y')
        beam.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = length * cross_section * member_depth * steel_density
    
    return beam

# Create all members
beam_objects = {}
for i, (start_id, end_id, cs, is_top) in enumerate(members):
    name = f"Beam_{start_id}{end_id}"
    beam = create_member(name, nodes[start_id], nodes[end_id], cs)
    beam_objects[(start_id, end_id)] = beam

# Create fixed constraints at joints
def create_fixed_constraint(name, obj_a, obj_b, location):
    """Create fixed constraint between two objects at location"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    # Disable breaking for rigidity
    constraint.use_breaking = False
    constraint.breaking_threshold = 10000.0
    
    return empty

# Define joint connections (nodes where members meet)
joints = {
    'A': [('A','B'), ('F','G')],  # Actually A connects to bottom chord start and vertical?
    'B': [('A','B'), ('B','C'), ('B','G'), ('C','G')],
    'C': [('B','C'), ('C','D'), ('C','G'), ('C','I'), ('C','H')],
    'D': [('C','D'), ('D','E'), ('D','I'), ('C','I')],
    'E': [('D','E'), ('I','J')],
    'F': [('F','G')],  # Left top start
    'G': [('F','G'), ('G','H'), ('B','G'), ('C','G')],
    'H': [('G','H'), ('H','I'), ('C','H')],
    'I': [('H','I'), ('I','J'), ('D','I'), ('C','I')],
    'J': [('I','J')]   # Right top end
}

# Create constraints for each joint with multiple members
constraint_count = 0
for joint_id, member_list in joints.items():
    if len(member_list) > 1:
        # Connect first member to all others
        primary_beam = beam_objects[member_list[0]]
        for i in range(1, len(member_list)):
            secondary_beam = beam_objects[member_list[i]]
            constraint_name = f"Fixed_{joint_id}_{i}"
            create_fixed_constraint(
                constraint_name,
                primary_beam,
                secondary_beam,
                nodes[joint_id]
            )
            constraint_count += 1

# Create supports (passive rigid bodies at ends)
bpy.ops.mesh.primitive_cube_add(size=0.5, location=nodes['A'])
support_a = bpy.context.active_object
support_a.name = "Support_A"
bpy.ops.rigidbody.object_add()
support_a.rigid_body.type = 'PASSIVE'

bpy.ops.mesh.primitive_cube_add(size=0.5, location=nodes['E'])
support_e = bpy.context.active_object
support_e.name = "Support_E"
bpy.ops.rigidbody.object_add()
support_e.rigid_body.type = 'PASSIVE'

# Constrain bottom chord ends to supports
create_fixed_constraint("SupportFix_A", beam_objects[('A','B')], support_a, nodes['A'])
create_fixed_constraint("SupportFix_E", beam_objects[('D','E')], support_e, nodes['E'])

# Create load applicators at top chord nodes
top_nodes_for_load = ['F', 'G', 'H', 'I', 'J']  # All top chord nodes
for node_id in top_nodes_for_load:
    loc = nodes[node_id]
    
    # Create small invisible mass for load
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=loc)
    load_obj = bpy.context.active_object
    load_obj.name = f"Load_{node_id}"
    load_obj.hide_render = True
    
    # Add rigid body with high mass
    bpy.ops.rigidbody.object_add()
    load_obj.rigid_body.mass = load_per_node_kg
    
    # Create motor constraint to apply downward force
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    motor_empty = bpy.context.active_object
    motor_empty.name = f"Motor_{node_id}"
    
    bpy.ops.rigidbody.constraint_add()
    motor = motor_empty.rigid_body_constraint
    motor.type = 'MOTOR'
    motor.object1 = load_obj
    motor.use_limit_lin_z = True
    motor.limit_lin_z_lower = 0
    motor.limit_lin_z_upper = 0
    motor.use_motor_lin = True
    motor.motor_lin_target_velocity = -1.0  # Downward
    motor.motor_lin_max_impulse = force_per_node
    
    # Connect load to nearest top chord member
    # Find which top chord member this node belongs to
    for (start, end, cs, is_top) in members:
        if is_top and (start == node_id or end == node_id):
            top_member = beam_objects[(start, end)]
            create_fixed_constraint(
                f"LoadAttach_{node_id}",
                load_obj,
                top_member,
                loc
            )
            break

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

print(f"Created Fink truss with {len(members)} members and {constraint_count} fixed constraints")
print(f"Load: {total_load_kg}kg distributed to {len(top_nodes_for_load)} nodes")
print(f"Apex height: {apex_height:.3f}m")