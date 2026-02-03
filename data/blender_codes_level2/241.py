import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 17.0
num_panels = 8
panel_length = span / num_panels
truss_height = 3.0
bottom_chord_z = 5.0
top_chord_z = bottom_chord_z + truss_height
cross_section = 0.2
beam_mass = 0.1
empty_mass = 1.0
total_load_kg = 1700
gravity = 9.8
total_force = total_load_kg * gravity
num_loaded_nodes = 7  # interior top nodes (T1 to T7)
force_per_node = total_force / num_loaded_nodes
column_height = bottom_chord_z
simulation_frames = 100
damping = 0.9

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(span/2, 0, 0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set world physics
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.damping = damping

# Node positions
nodes = {}
for i in range(num_panels + 1):
    x = i * panel_length
    nodes[f'B{i}'] = Vector((x, 0, bottom_chord_z))  # bottom chord
    nodes[f'T{i}'] = Vector((x, 0, top_chord_z))     # top chord

# Create empties at nodes
empties = {}
for name, loc in nodes.items():
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    empty = bpy.context.active_object
    empty.name = f'Empty_{name}'
    bpy.ops.rigidbody.object_add()
    empty.rigid_body.mass = empty_mass
    empty.rigid_body.collision_shape = 'SPHERE'
    empty.rigid_body.linear_damping = 0.5
    empty.rigid_body.angular_damping = 0.5
    empties[name] = empty

# Function to create a beam between two points
def create_beam(p1, p2, name, mass=beam_mass):
    # Midpoint and direction
    mid = (p1 + p2) / 2
    dir_vec = p2 - p1
    length = dir_vec.length
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: default cube is 2x2x2, so to get cross_section x cross_section x length,
    # scale by (cross_section/2, cross_section/2, length/2)
    beam.scale = (cross_section/2, cross_section/2, length/2)
    
    # Rotate to align local Z with direction vector
    # Default cube local Z is global Z, so we rotate to match dir_vec
    z_axis = Vector((0, 0, 1))
    rot_quat = z_axis.rotation_difference(dir_vec)
    beam.rotation_mode = 'QUATERNION'
    beam.rotation_quaternion = rot_quat
    
    # Apply scale and rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.mass = mass
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.linear_damping = 0.5
    beam.rigid_body.angular_damping = 0.5
    
    return beam

# Create top chord members
top_beams = []
for i in range(num_panels):
    p1 = nodes[f'T{i}']
    p2 = nodes[f'T{i+1}']
    beam = create_beam(p1, p2, f'TopChord_{i}')
    top_beams.append(beam)

# Create bottom chord members
bottom_beams = []
for i in range(num_panels):
    p1 = nodes[f'B{i}']
    p2 = nodes[f'B{i+1}']
    beam = create_beam(p1, p2, f'BottomChord_{i}')
    bottom_beams.append(beam)

# Create vertical members (interior, T_i to B_i for i=1..7)
vertical_beams = []
for i in range(1, num_panels):
    p1 = nodes[f'T{i}']
    p2 = nodes[f'B{i}']
    beam = create_beam(p1, p2, f'Vertical_{i}')
    vertical_beams.append(beam)

# Create diagonal members (B_i to T_{i+1})
diagonal_beams = []
for i in range(num_panels):
    p1 = nodes[f'B{i}']
    p2 = nodes[f'T{i+1}']
    beam = create_beam(p1, p2, f'Diagonal_{i}')
    diagonal_beams.append(beam)

# Create support columns (B0 and B8 to ground)
support_beams = []
for i in [0, num_panels]:
    p1 = nodes[f'B{i}']
    p2 = Vector((p1.x, p1.y, 0))
    beam = create_beam(p1, p2, f'Column_{i}', mass=empty_mass*10)
    support_beams.append(beam)
    # Fix column to ground with fixed constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=p2)
    ground_anchor = bpy.context.active_object
    ground_anchor.name = f'GroundAnchor_{i}'
    bpy.ops.rigidbody.object_add()
    ground_anchor.rigid_body.type = 'PASSIVE'
    # Constraint between column and ground anchor
    bpy.ops.object.select_all(action='DESELECT')
    beam.select_set(True)
    ground_anchor.select_set(True)
    bpy.context.view_layer.objects.active = beam
    bpy.ops.rigidbody.constraint_add(type='FIXED')

# Function to add fixed constraint between two objects
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    obj_b.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add(type='FIXED')

# Connect beams to node empties
for i in range(num_panels + 1):
    # Each node empty connects to all beams that meet at that node
    empty_T = empties[f'T{i}']
    empty_B = empties[f'B{i}']
    
    # Top chord connections
    if i < num_panels:
        beam = top_beams[i]
        add_fixed_constraint(empty_T, beam)
    if i > 0:
        beam = top_beams[i-1]
        add_fixed_constraint(empty_T, beam)
    
    # Bottom chord connections
    if i < num_panels:
        beam = bottom_beams[i]
        add_fixed_constraint(empty_B, beam)
    if i > 0:
        beam = bottom_beams[i-1]
        add_fixed_constraint(empty_B, beam)
    
    # Vertical connections (only for interior)
    if 0 < i < num_panels:
        beam = vertical_beams[i-1]
        add_fixed_constraint(empty_T, beam)
        add_fixed_constraint(empty_B, beam)
    
    # Diagonal connections
    if i < num_panels:
        beam = diagonal_beams[i]
        add_fixed_constraint(empty_B, beam)
        add_fixed_constraint(empties[f'T{i+1}'], beam)
    if i > 0:
        beam = diagonal_beams[i-1]
        add_fixed_constraint(empty_T, beam)
        add_fixed_constraint(empties[f'B{i-1}'], beam)
    
    # Column connections
    if i in [0, num_panels]:
        beam = support_beams[0] if i==0 else support_beams[1]
        add_fixed_constraint(empty_B, beam)

# Apply forces to interior top nodes (T1 to T7)
for i in range(1, num_panels):
    empty = empties[f'T{i}']
    # Add a constant force in negative Z direction
    empty.rigid_body.use_gravity = False  # We'll apply force manually
    # In Blender, constant force is applied via rigid body settings
    # We'll use a force field limited to the empty's location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=empty.location)
    force_empty = bpy.context.active_object
    force_empty.name = f'Force_T{i}'
    bpy.ops.object.forcefield_toggle()
    force_empty.field.type = 'FORCE'
    force_empty.field.strength = -force_per_node  # Negative for downward
    force_empty.field.use_max_distance = True
    force_empty.field.distance_max = 0.5  # Only affect nearby objects
    # Parent force field to the node empty so it moves with it
    force_empty.parent = empty
    force_empty.matrix_parent_inverse = empty.matrix_world.inverted()

# Set simulation end frame
bpy.context.scene.frame_end = simulation_frames

# Optional: run simulation and export visualization
# bpy.ops.ptcache.bake_all(bake=True)