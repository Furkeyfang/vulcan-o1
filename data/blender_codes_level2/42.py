import bpy
import math
from mathutils import Vector

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_span = 5.0
truss_height = 1.0
chord_cs = 0.1
brace_cs = 0.05
num_panels = 5
panel_width = base_span / num_panels
top_nodes_x = [0.5 + i * panel_width for i in range(num_panels)]
bottom_nodes_x = [i * panel_width for i in range(num_panels + 1)]
total_load = 3433.5
load_per_node = total_load / len(top_nodes_x)
joint_tol = 0.01

# Store created objects for constraint creation
objects_by_position = {}

def create_beam(start, end, cross_section, name, is_passive=False):
    """Create a beam between two points"""
    # Calculate beam properties
    length = (Vector(end) - Vector(start)).length
    direction = (Vector(end) - Vector(start)).normalized()
    center = (Vector(start) + Vector(end)) / 2
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length in X, cross-section in Y/Z (cube default 1x1x1)
    beam.scale = (length/2, cross_section/2, cross_section/2)
    
    # Rotate to align with direction
    if direction.length > 0:
        # Default cube axis is (1,0,0), rotate to match direction
        rot_axis = Vector((1,0,0)).cross(direction)
        if rot_axis.length > 0:
            angle = Vector((1,0,0)).angle(direction)
            beam.rotation_euler = rot_axis.normalized().to_track_quat('Z', 'Y').to_euler()
            beam.rotation_euler.z = angle  # Simplified rotation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE' if is_passive else 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = length * cross_section * cross_section * 7800  # Steel density kg/m³
    
    return beam

# Create bottom chord (segments between bottom nodes)
bottom_chords = []
for i in range(len(bottom_nodes_x)-1):
    start = (bottom_nodes_x[i], 0.0, 0.0)
    end = (bottom_nodes_x[i+1], 0.0, 0.0)
    is_passive = (i == 0 or i == len(bottom_nodes_x)-2)  # End segments as supports
    chord = create_beam(start, end, chord_cs, f"Bottom_Chord_{i}", is_passive)
    bottom_chords.append(chord)
    # Store for constraints
    objects_by_position[tuple(start)] = objects_by_position.get(tuple(start), []) + [chord]
    objects_by_position[tuple(end)] = objects_by_position.get(tuple(end), []) + [chord]

# Create top chord (segments between top nodes)
top_chords = []
for i in range(len(top_nodes_x)-1):
    start = (top_nodes_x[i], 0.0, truss_height)
    end = (top_nodes_x[i+1], 0.0, truss_height)
    chord = create_beam(start, end, chord_cs, f"Top_Chord_{i}")
    top_chords.append(chord)
    objects_by_position[tuple(start)] = objects_by_position.get(tuple(start), []) + [chord]
    objects_by_position[tuple(end)] = objects_by_position.get(tuple(end), []) + [chord]
    
    # Add downward force to top chords (distributed load)
    chord.rigid_body.constant_force = (0, 0, -load_per_node/2)  # Half load to each adjacent node

# Create diagonals (bottom nodes to adjacent top nodes)
diagonals = []
for i, bottom_x in enumerate(bottom_nodes_x):
    # Connect to left top node if exists
    if i > 0:
        top_x = top_nodes_x[i-1]
        start = (bottom_x, 0.0, 0.0)
        end = (top_x, 0.0, truss_height)
        diag = create_beam(start, end, brace_cs, f"Diagonal_L_{i}")
        diagonals.append(diag)
        objects_by_position[tuple(start)] = objects_by_position.get(tuple(start), []) + [diag]
        objects_by_position[tuple(end)] = objects_by_position.get(tuple(end), []) + [diag]
    
    # Connect to right top node if exists
    if i < len(bottom_nodes_x)-1:
        top_x = top_nodes_x[i]
        start = (bottom_x, 0.0, 0.0)
        end = (top_x, 0.0, truss_height)
        diag = create_beam(start, end, brace_cs, f"Diagonal_R_{i}")
        diagonals.append(diag)
        objects_by_position[tuple(start)] = objects_by_position.get(tuple(start), []) + [diag]
        objects_by_position[tuple(end)] = objects_by_position.get(tuple(end), []) + [diag]

# Create fixed constraints at joints
for pos_str, objs in objects_by_position.items():
    if len(objs) < 2:
        continue
    
    # Create constraint between first object and all others
    obj1 = objs[0]
    for obj2 in objs[1:]:
        # Create empty for constraint
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos_str)
        constraint_empty = bpy.context.active_object
        constraint_empty.name = f"Fixed_{pos_str[0]:.1f}_{pos_str[2]:.1f}_{len(objs)}"
        
        # Add rigid body constraint
        bpy.ops.rigidbody.constraint_add()
        constraint_empty.rigid_body_constraint.type = 'FIXED'
        constraint_empty.rigid_body_constraint.object1 = obj1
        constraint_empty.rigid_body_constraint.object2 = obj2

# Set world physics
bpy.context.scene.gravity = Vector((0, 0, -9.81))
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print(f"Truss constructed with {len(bottom_chords)} bottom chords, {len(top_chords)} top chords, {len(diagonals)} diagonals")
print(f"Total load: {total_load}N distributed as {load_per_node}N per top node")