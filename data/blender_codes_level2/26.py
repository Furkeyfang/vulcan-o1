import bpy
import math
from mathutils import Vector, Matrix

# ====================
# PARAMETERS FROM SUMMARY
# ====================
span = 5.0
n_panels = 17
panel_spacing = span / n_panels
diagonal_length = panel_spacing / math.cos(math.radians(60))
truss_depth = diagonal_length * math.sin(math.radians(60))
bottom_chord_z = 0.5
top_chord_z = bottom_chord_z + truss_depth
chord_cross_section = (0.1, 0.1)
diagonal_cross_section = (0.08, 0.08)
platform_dim = (5.0, 2.0, 0.05)
platform_z = 1.0
platform_y_offset = -1.0
load_mass_kg = 450
gravity = 9.81
force_newtons = load_mass_kg * gravity
material_density = 7800

# ====================
# CLEAR SCENE
# ====================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ====================
# HELPER FUNCTIONS
# ====================
def create_member(name, start, end, cross_section, is_diagonal=False):
    """Create a cuboid member between two points with given cross-section."""
    # Calculate local orientation
    vec = Vector(end) - Vector(start)
    length = vec.length
    center = (Vector(start) + Vector(end)) / 2
    
    # Create cube and scale
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    
    # Apply scaling: X=length, Y=cross_section[0], Z=cross_section[1]
    obj.scale = (length/2, cross_section[0]/2, cross_section[1]/2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Rotate to align with vector
    if length > 0.001:  # Avoid zero-length vectors
        # Default cube local Z is up, we want local X along the member
        up = Vector((0, 0, 1))
        rot_quat = vec.to_track_quat('X', 'Z')
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot_quat
    
    # Move to center position
    obj.location = center
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.mass = material_density * (length * cross_section[0] * cross_section[1])
    obj.rigid_body.collision_shape = 'BOX'
    
    return obj

def create_fixed_constraint(obj_a, obj_b):
    """Create a fixed rigid body constraint between two objects."""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    empty.location = (Vector(obj_a.location) + Vector(obj_b.location)) / 2
    
    # Parent constraint to scene
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# ====================
# CREATE TRUSS MEMBERS
# ====================
members = []
joint_objects = {}  # Maps joint position to list of connected members

# Generate joint positions
bottom_joints = [(i * panel_spacing, 0.0, bottom_chord_z) for i in range(n_panels + 1)]
top_joints = [(i * panel_spacing, 0.0, top_chord_z) for i in range(n_panels + 1)]

# Create chord members
for i in range(n_panels):
    # Bottom chord segment
    name = f"Bottom_Chord_{i}"
    obj = create_member(name, bottom_joints[i], bottom_joints[i+1], chord_cross_section)
    members.append(obj)
    # Register with joints
    joint_objects.setdefault(bottom_joints[i], []).append(obj)
    joint_objects.setdefault(bottom_joints[i+1], []).append(obj)
    
    # Top chord segment
    name = f"Top_Chord_{i}"
    obj = create_member(name, top_joints[i], top_joints[i+1], chord_cross_section)
    members.append(obj)
    joint_objects.setdefault(top_joints[i], []).append(obj)
    joint_objects.setdefault(top_joints[i+1], []).append(obj)

# Create diagonal members (alternating pattern)
for i in range(n_panels):
    if i % 2 == 0:  # Even: bottom-left to top-right
        start, end = bottom_joints[i], top_joints[i+1]
    else:  # Odd: top-left to bottom-right
        start, end = top_joints[i], bottom_joints[i+1]
    
    name = f"Diagonal_{i}"
    obj = create_member(name, start, end, diagonal_cross_section, is_diagonal=True)
    members.append(obj)
    joint_objects.setdefault(start, []).append(obj)
    joint_objects.setdefault(end, []).append(obj)

# ====================
# CREATE PLATFORM
# ====================
bpy.ops.mesh.primitive_cube_add(size=1.0)
platform = bpy.context.active_object
platform.name = "Observation_Platform"
platform.scale = (platform_dim[0]/2, platform_dim[1]/2, platform_dim[2]/2)
bpy.ops.object.transform_apply(scale=True)
platform.location = (span/2, platform_y_offset + platform_dim[1]/2, platform_z)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass_kg  # Represents deck mass
platform.rigid_body.collision_shape = 'BOX'

# ====================
# CREATE FIXED CONSTRAINTS
# ====================
# 1. Truss joint constraints
for joint_pos, connected_objs in joint_objects.items():
    if len(connected_objs) >= 2:
        for i in range(len(connected_objs)-1):
            create_fixed_constraint(connected_objs[0], connected_objs[i+1])

# 2. Platform-to-top-chord constraints (attach at multiple points)
platform_attach_points = 5  # Attach at 5 points along span
for i in range(platform_attach_points):
    x = (i/(platform_attach_points-1)) * span if platform_attach_points > 1 else span/2
    # Find nearest top chord member
    for obj in members:
        if "Top_Chord" in obj.name:
            # Check if x coordinate within member bounds
            if abs(obj.location.x - x) <= panel_spacing/2:
                create_fixed_constraint(obj, platform)
                break

# ====================
# APPLY LOADS & BOUNDARY CONDITIONS
# ====================
# Apply downward force on platform (in negative Z direction)
platform.rigid_body.force_type = 'FORCE'
platform.rigid_body.force = (0, 0, -force_newtons)

# Fix ends of bottom chord (simply supported boundary conditions)
for obj in members:
    if "Bottom_Chord_0" in obj.name or f"Bottom_Chord_{n_panels-1}" in obj.name:
        obj.rigid_body.type = 'PASSIVE'  # Fixed supports

# ====================
# SET UP PHYSICS WORLD
# ====================
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100  # Verify stability for 100 frames

print(f"Warren Truss constructed with {len(members)} members")
print(f"Platform load: {force_newtons:.1f} N downward")
print(f"Simulation ready - run for {bpy.context.scene.frame_end} frames")