import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define parameters from summary
span_length = 11.0
truss_height = 1.5
truss_width = 2.0
num_segments = 5
segment_length = 2.2

cross_section = 0.2
member_depth = cross_section
member_width = cross_section

bottom_joints_x = [0.0, 2.2, 4.4, 6.6, 8.8, 11.0]
top_joints_x = [0.0, 2.2, 4.4, 6.6, 8.8, 11.0]
truss_y_positions = [-1.0, 1.0]

total_load_kg = 850.0
top_chord_segments = 10
mass_per_top_segment = 85.0
mass_other_members = 5.0

simulation_frames = 100
gravity = 9.81

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, -gravity)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Store objects by joint for constraint creation
joint_objects = {}

def create_beam(start, end, name, mass, is_passive=False):
    """Create a beam between two points with proper orientation"""
    # Calculate beam properties
    direction = Vector(end) - Vector(start)
    length = direction.length
    center = (Vector(start) + Vector(end)) / 2
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: cube is 2×2×2, so divide by 2
    beam.scale = (length / 2, member_width / 2, member_depth / 2)
    
    # Align with direction vector
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('Z', 'Y')
    beam.rotation_euler = rot_quat.to_euler()
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'PASSIVE' if is_passive else 'ACTIVE'
    beam.rigid_body.mass = mass
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.friction = 0.5
    beam.rigid_body.restitution = 0.1
    
    return beam

def add_to_joint_dict(obj, joint_key):
    """Register object at a joint for later constraint creation"""
    if joint_key not in joint_objects:
        joint_objects[joint_key] = []
    joint_objects[joint_key].append(obj)

# Create trusses
for truss_idx, y_pos in enumerate(truss_y_positions):
    truss_prefix = f"Truss{truss_idx}_"
    
    # Create bottom chord (horizontal beams)
    for i in range(num_segments):
        start = (bottom_joints_x[i], y_pos, 0)
        end = (bottom_joints_x[i+1], y_pos, 0)
        name = f"{truss_prefix}BottomChord_{i}"
        
        # End segments are passive supports
        is_passive = (i == 0 or i == num_segments-1)
        mass = mass_other_members
        
        beam = create_beam(start, end, name, mass, is_passive)
        
        # Register at joints
        add_to_joint_dict(beam, (bottom_joints_x[i], y_pos, 0))
        add_to_joint_dict(beam, (bottom_joints_x[i+1], y_pos, 0))
    
    # Create top chord (horizontal beams)
    for i in range(num_segments):
        start = (top_joints_x[i], y_pos, truss_height)
        end = (top_joints_x[i+1], y_pos, truss_height)
        name = f"{truss_prefix}TopChord_{i}"
        
        beam = create_beam(start, end, name, mass_per_top_segment, False)
        
        # Register at joints
        add_to_joint_dict(beam, (top_joints_x[i], y_pos, truss_height))
        add_to_joint_dict(beam, (top_joints_x[i+1], y_pos, truss_height))
    
    # Create vertical members
    for i in range(len(bottom_joints_x)):
        start = (bottom_joints_x[i], y_pos, 0)
        end = (top_joints_x[i], y_pos, truss_height)
        name = f"{truss_prefix}Vertical_{i}"
        
        beam = create_beam(start, end, name, mass_other_members, False)
        
        # Register at joints
        add_to_joint_dict(beam, (bottom_joints_x[i], y_pos, 0))
        add_to_joint_dict(beam, (top_joints_x[i], y_pos, truss_height))
    
    # Create diagonal members (alternating Pratt pattern)
    diagonals = [
        # Bay 0-1: top-left to bottom-right
        ((top_joints_x[0], y_pos, truss_height), (bottom_joints_x[1], y_pos, 0)),
        # Bay 1-2: top-right to bottom-left  
        ((top_joints_x[2], y_pos, truss_height), (bottom_joints_x[1], y_pos, 0)),
        # Bay 2-3: top-left to bottom-right
        ((top_joints_x[2], y_pos, truss_height), (bottom_joints_x[3], y_pos, 0)),
        # Bay 3-4: top-right to bottom-left
        ((top_joints_x[4], y_pos, truss_height), (bottom_joints_x[3], y_pos, 0)),
        # Bay 4-5: top-left to bottom-right
        ((top_joints_x[4], y_pos, truss_height), (bottom_joints_x[5], y_pos, 0))
    ]
    
    for i, (start, end) in enumerate(diagonals):
        name = f"{truss_prefix}Diagonal_{i}"
        beam = create_beam(start, end, name, mass_other_members, False)
        
        # Register at joints
        add_to_joint_dict(beam, start)
        add_to_joint_dict(beam, end)

# Create lateral bracing (connect trusses at joints)
for x in bottom_joints_x:
    for z in [0, truss_height]:
        start = (x, truss_y_positions[0], z)
        end = (x, truss_y_positions[1], z)
        name = f"Lateral_X{x}_Z{z}"
        
        beam = create_beam(start, end, name, mass_other_members, False)
        
        # Register at both ends
        add_to_joint_dict(beam, start)
        add_to_joint_dict(beam, end)

# Create fixed constraints at joints
for joint_key, objects in joint_objects.items():
    if len(objects) < 2:
        continue
    
    # Create constraint between first object and all others at this joint
    base_obj = objects[0]
    for other_obj in objects[1:]:
        # Select objects
        bpy.ops.object.select_all(action='DESELECT')
        base_obj.select_set(True)
        other_obj.select_set(True)
        bpy.context.view_layer.objects.active = base_obj
        
        # Add fixed constraint
        bpy.ops.rigidbody.constraint_add()
        constraint = bpy.context.active_object
        constraint.name = f"Fixed_{joint_key[0]:.1f}_{joint_key[1]:.1f}_{joint_key[2]:.1f}"
        constraint.empty_display_type = 'ARROWS'
        constraint.location = joint_key
        
        # Configure constraint
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = base_obj
        constraint.rigid_body_constraint.object2 = other_obj

# Set simulation length
bpy.context.scene.frame_end = simulation_frames

print(f"Pratt truss bridge created with {len(joint_objects)} joints")
print(f"Total load: {total_load_kg}kg distributed across {top_chord_segments} top chord segments")