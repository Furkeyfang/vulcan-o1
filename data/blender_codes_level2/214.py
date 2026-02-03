import bpy
import math
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
span = 8.0
slope_deg = 20.0
slope_rad = math.radians(slope_deg)
total_height = span * math.tan(slope_rad)
cross_section = 0.2
web_spacing = 2.0
joint_margin = 0.05
total_load_N = 5886.0
nodes_count = 5
force_per_node = total_load_N / nodes_count
support_size = (0.3, 0.3, 0.3)
simulation_frames = 100
max_allowed_displacement = 0.1
damping = 0.5

# Node positions (X, Y, Z) - Y=0 for planar truss
nodes = {
    'B0': Vector((0.0, 0.0, 0.0)),           # Bottom left
    'B2': Vector((2.0, 0.0, 0.0)),           # Bottom at 2m
    'B4': Vector((4.0, 0.0, 0.0)),           # Bottom at 4m
    'B6': Vector((6.0, 0.0, 0.0)),           # Bottom at 6m
    'B8': Vector((8.0, 0.0, 0.0)),           # Bottom right
    
    'T0': Vector((0.0, 0.0, 0.0)),           # Top left (same as B0)
    'T2': Vector((2.0, 0.0, 2.0 * math.tan(slope_rad))),  # 0.72794
    'T4': Vector((4.0, 0.0, 4.0 * math.tan(slope_rad))),  # 1.45588
    'T6': Vector((6.0, 0.0, 6.0 * math.tan(slope_rad))),  # 2.18382
    'T8': Vector((8.0, 0.0, total_height))   # Top right (2.91176)
}

# Member definitions: (start_node, end_node)
members = [
    # Bottom chord segments
    ('B0', 'B2'), ('B2', 'B4'), ('B4', 'B6'), ('B6', 'B8'),
    # Top chord segments
    ('T0', 'T2'), ('T2', 'T4'), ('T4', 'T6'), ('T6', 'T8'),
    # Vertical webs
    ('B2', 'T2'), ('B4', 'T4'), ('B6', 'T6'),
    # Diagonal webs (alternating)
    ('B2', 'T4'), ('T4', 'B6')
]

# Function to create beam between two points
def create_beam(start, end, name, cross_section=0.2):
    """Create a rectangular beam from start to end point"""
    direction = end - start
    length = direction.length
    mid_point = (start + end) / 2
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mid_point)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: cross-section in X/Y, length in Z
    beam.scale = (cross_section/2, cross_section/2, length/2)
    
    # Rotate to align with direction vector
    if length > 0.001:  # Avoid division by zero
        # Default cube orientation has local Z as length
        z_axis = Vector((0, 0, 1))
        rot_quat = z_axis.rotation_difference(direction.normalized())
        beam.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.mass = 50.0  # Approximate mass for steel
    beam.rigid_body.use_margin = True
    beam.rigid_body.collision_margin = 0.01
    beam.rigid_body.linear_damping = damping
    beam.rigid_body.angular_damping = damping
    
    return beam

# Function to create fixed constraint between two objects
def create_fixed_constraint(obj_a, obj_b, name):
    """Create a fixed rigid body constraint between two objects"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link objects
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return empty

# Create all truss members
beam_objects = {}
for i, (start_name, end_name) in enumerate(members):
    beam_name = f"Beam_{start_name}_{end_name}"
    beam = create_beam(nodes[start_name], nodes[end_name], beam_name, cross_section)
    beam_objects[(start_name, end_name)] = beam

# Create supports (passive rigid bodies)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=nodes['B0'])
support_left = bpy.context.active_object
support_left.name = "Support_Left"
support_left.scale = Vector(support_size) / 2
bpy.ops.rigidbody.object_add()
support_left.rigid_body.type = 'PASSIVE'

bpy.ops.mesh.primitive_cube_add(size=1.0, location=nodes['B8'])
support_right = bpy.context.active_object
support_right.name = "Support_Right"
support_right.scale = Vector(support_size) / 2
bpy.ops.rigidbody.object_add()
support_right.rigid_body.type = 'PASSIVE'

# Create fixed constraints at all joints
constraints = []
joint_members = {}  # Map node name to list of connected beams

# Build connectivity map
for (start, end), beam in beam_objects.items():
    joint_members.setdefault(start, []).append(beam)
    joint_members.setdefault(end, []).append(beam)

# Add supports to connectivity
joint_members['B0'].append(support_left)
joint_members['B8'].append(support_right)

# Create constraints for each joint
for node_name, connected_objects in joint_members.items():
    if len(connected_objects) > 1:
        # Connect first object to all others
        base_obj = connected_objects[0]
        for other_obj in connected_objects[1:]:
            if other_obj != base_obj:
                constraint_name = f"Constraint_{node_name}_{base_obj.name}_{other_obj.name}"
                constraint = create_fixed_constraint(base_obj, other_obj, constraint_name)
                constraints.append(constraint)

# Apply loads to top chord nodes
top_nodes = ['T0', 'T2', 'T4', 'T6', 'T8']
for node_name in top_nodes:
    # Find all beams connected to this top node
    connected_beams = []
    for (start, end), beam in beam_objects.items():
        if start == node_name or end == node_name:
            connected_beams.append(beam)
    
    # Apply downward force to each connected beam
    for beam in connected_beams:
        # Force is distributed among connected beams
        force_magnitude = force_per_node / len(connected_beams)
        force_vector = Vector((0, 0, -force_magnitude))
        
        # Apply force at center (approximation)
        beam.rigid_body.force = force_vector

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Keyframe initial positions for displacement tracking
initial_positions = {}
all_objects = list(beam_objects.values()) + [support_left, support_right] + constraints
for obj in all_objects:
    if obj.type == 'MESH':  # Only track mesh objects
        initial_positions[obj.name] = obj.matrix_world.translation.copy()
        obj.keyframe_insert(data_path="location", frame=1)

print("Truss construction complete. Simulation ready.")
print(f"Total load: {total_load_N} N distributed across {nodes_count} nodes")
print(f"Expected maximum displacement limit: {max_allowed_displacement} m")