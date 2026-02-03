import bpy
import math
from mathutils import Matrix, Vector

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Set gravity for realistic simulation
bpy.context.scene.gravity = (0, 0, -9.81)

# ===== PARAMETERS =====
# Foundation
foundation_size = (4.0, 4.0, 1.0)
foundation_loc = (0.0, 0.0, 0.5)

# Tower
tower_height = 24.0
tower_width = 2.0
beam_cross_section = 0.2
beam_length_horizontal = 2.0
beam_length_diagonal = 2.828
vertical_spacing = 2.0
num_levels = 13

# Platform
platform_size = (2.0, 2.0, 0.5)
platform_loc = (0.0, 0.0, 25.25)

# Load
load_mass = 1500.0
load_size = (1.0, 1.0, 1.0)
load_loc = (0.0, 0.0, 26.0)

# Joint sphere size
joint_radius = 0.1

# ===== HELPER FUNCTIONS =====
def create_beam(start, end, name, cross_section=0.2):
    """Create a beam between two points with square cross-section"""
    # Calculate beam properties
    direction = Vector(end) - Vector(start)
    length = direction.length
    center = (Vector(start) + Vector(end)) / 2
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: length in local X, cross-section in Y and Z
    beam.scale = (length/2, cross_section/2, cross_section/2)
    
    # Rotate to align with direction
    if length > 0:
        # Default cube faces +X direction
        rot_quat = Vector((1, 0, 0)).rotation_difference(direction)
        beam.rotation_mode = 'QUATERNION'
        beam.rotation_quaternion = rot_quat
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = 'ACTIVE'
    beam.rigid_body.collision_shape = 'BOX'
    beam.rigid_body.mass = length * cross_section**2 * 7850  # Steel density (kg/m³)
    
    return beam

def create_joint_sphere(location, name):
    """Create a joint sphere for constraint connections"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=joint_radius, location=location)
    joint = bpy.context.active_object
    joint.name = name
    joint.hide_render = True
    joint.hide_viewport = True
    
    # Add rigid body (passive for constraints)
    bpy.ops.rigidbody.object_add()
    joint.rigid_body.type = 'PASSIVE'
    joint.rigid_body.collision_shape = 'SPHERE'
    
    return joint

def add_fixed_constraint(obj_a, obj_b, name):
    """Add fixed constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_a.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    return constraint_empty

# ===== CREATE FOUNDATION =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=foundation_loc)
foundation = bpy.context.active_object
foundation.name = "Foundation"
foundation.scale = foundation_size
bpy.ops.rigidbody.object_add()
foundation.rigid_body.type = 'PASSIVE'

# ===== CREATE TOWER STRUCTURE =====
joints = {}  # Store joint spheres by coordinates
beams = []   # Store all beams

# Generate joint positions and create spheres
for level in range(num_levels):
    z = 1.0 + level * vertical_spacing
    for x in [-tower_width/2, tower_width/2]:
        for y in [-tower_width/2, tower_width/2]:
            loc = (x, y, z)
            key = f"J_{x:.1f}_{y:.1f}_{z:.1f}"
            joints[key] = create_joint_sphere(loc, key)

# Create horizontal beams
for level in range(num_levels):
    z = 1.0 + level * vertical_spacing
    
    # X-direction beams (front and back)
    for y in [-tower_width/2, tower_width/2]:
        start = (-tower_width/2, y, z)
        end = (tower_width/2, y, z)
        name = f"Beam_X_y{y:.1f}_z{z:.1f}"
        beam = create_beam(start, end, name, beam_cross_section)
        beams.append(beam)
    
    # Y-direction beams (left and right)
    for x in [-tower_width/2, tower_width/2]:
        start = (x, -tower_width/2, z)
        end = (x, tower_width/2, z)
        name = f"Beam_Y_x{x:.1f}_z{z:.1f}"
        beam = create_beam(start, end, name, beam_cross_section)
        beams.append(beam)

# Create diagonal beams (alternating pattern)
for level in range(num_levels - 1):
    z_bottom = 1.0 + level * vertical_spacing
    z_top = z_bottom + vertical_spacing
    
    # Pattern 1: (-1,-1) to (1,1)
    start = (-tower_width/2, -tower_width/2, z_bottom)
    end = (tower_width/2, tower_width/2, z_top)
    name = f"Beam_D1_z{z_bottom:.1f}"
    beam = create_beam(start, end, name, beam_cross_section)
    beams.append(beam)
    
    # Pattern 2: (1,-1) to (-1,1)
    start = (tower_width/2, -tower_width/2, z_bottom)
    end = (-tower_width/2, tower_width/2, z_top)
    name = f"Beam_D2_z{z_bottom:.1f}"
    beam = create_beam(start, end, name, beam_cross_section)
    beams.append(beam)

# ===== CREATE CONSTRAINTS =====
# Connect foundation to bottom joints
for y in [-tower_width/2, tower_width/2]:
    for x in [-tower_width/2, tower_width/2]:
        key = f"J_{x:.1f}_{y:.1f}_1.0"
        if key in joints:
            add_fixed_constraint(foundation, joints[key], f"Con_Found_{key}")

# Connect beams to joints
for beam in beams:
    # Get beam endpoints (simplified - using transformed bounding box)
    beam_matrix = beam.matrix_world
    local_ends = [Vector((-beam.scale.x, 0, 0)), Vector((beam.scale.x, 0, 0))]
    world_ends = [beam_matrix @ end for end in local_ends]
    
    # Find nearest joint for each endpoint
    for i, end_point in enumerate(world_ends):
        nearest_joint = None
        min_dist = float('inf')
        
        for joint_key, joint_obj in joints.items():
            dist = (joint_obj.location - end_point).length
            if dist < min_dist and dist < 0.5:  # Tolerance
                min_dist = dist
                nearest_joint = joint_obj
        
        if nearest_joint:
            add_fixed_constraint(beam, nearest_joint, f"Con_{beam.name}_end{i}")

# Connect top joints together (platform support ring)
top_z = 1.0 + (num_levels - 1) * vertical_spacing
top_joints = []
for key, joint in joints.items():
    if f"_{top_z:.1f}" in key:
        top_joints.append(joint)

# Connect top joints in a loop
for i in range(len(top_joints)):
    j = (i + 1) % len(top_joints)
    add_fixed_constraint(top_joints[i], top_joints[j], f"Con_TopRing_{i}")

# ===== CREATE PLATFORM =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_size
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'

# Connect platform to top joints
for joint in top_joints:
    add_fixed_constraint(platform, joint, f"Con_Platform_{joint.name}")

# ===== CREATE LOAD =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_size
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Connect load to platform
add_fixed_constraint(load, platform, "Con_Load_Platform")

# ===== SIMULATION SETUP =====
# Set simulation end frame
bpy.context.scene.frame_end = 500

# Set rigid body world settings for stability
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Lattice elevator tower constructed successfully")
print(f"Total beams: {len(beams)}")
print(f"Total joints: {len(joints)}")
print(f"Load mass: {load_mass} kg")