import bpy
import math
from mathutils import Vector, Matrix

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
span = 14.0
peak_height = 3.0
base_height = 1.0
cross_section_y = 0.2
cross_section_z = 0.2
node_A = Vector((0.0, 0.0, 1.0))
node_B = Vector((7.0, 0.0, 3.0))
node_C = Vector((14.0, 0.0, 1.0))
node_D = Vector((7.0, 0.0, 1.0))
top_left_length = 7.280109889280518
top_right_length = 7.280109889280518
bottom_left_length = 7.0
bottom_right_length = 7.0
vertical_length = 2.0
total_force_N = 12753.0
force_per_node = 4251.0
ground_z = 0.0

# Function to create a beam between two points
def create_beam(name, start, end, length, scale_y, scale_z):
    # Calculate midpoint and direction
    mid = (start + end) / 2
    direction = (end - start).normalized()
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Rotate to align with direction
    # Default cube forward is +X, so we rotate to match direction
    up = Vector((0, 0, 1))
    rot_quat = direction.to_track_quat('X', 'Z')
    beam.rotation_euler = rot_quat.to_euler()
    
    # Scale: length in X, cross-section in Y and Z
    beam.scale = (length, scale_y, scale_z)
    
    # Apply scale to mesh
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    return beam

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=span * 2, location=(span / 2, 0, ground_z))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (2, 2, 1)
bpy.ops.object.transform_apply(scale=True)

# Create truss members
top_left = create_beam("Top_Left", node_A, node_B, top_left_length, cross_section_y, cross_section_z)
top_right = create_beam("Top_Right", node_B, node_C, top_right_length, cross_section_y, cross_section_z)
bottom_left = create_beam("Bottom_Left", node_A, node_D, bottom_left_length, cross_section_y, cross_section_z)
bottom_right = create_beam("Bottom_Right", node_D, node_C, bottom_right_length, cross_section_y, cross_section_z)
vertical = create_beam("Vertical", node_D, node_B, vertical_length, cross_section_y, cross_section_z)

# Add rigid body physics
for obj in [top_left, top_right, bottom_left, bottom_right, vertical]:
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'ACTIVE'
    obj.rigid_body.mass = 100  # Approximate mass for steel (density 7850 kg/m³ * volume)
    obj.rigid_body.collision_shape = 'BOX'
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1

# Ground as passive rigid body
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

# Function to add fixed constraint between two objects at a point
def add_fixed_constraint(obj_a, obj_b, location):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{obj_a.name}_{obj_b.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    empty.rigid_body_constraint.type = 'FIXED'
    empty.rigid_body_constraint.object1 = obj_a
    empty.rigid_body_constraint.object2 = obj_b

# Add constraints at joints
add_fixed_constraint(top_left, bottom_left, node_A)   # Joint A
add_fixed_constraint(top_left, top_right, node_B)     # Joint B
add_fixed_constraint(top_left, vertical, node_B)
add_fixed_constraint(top_right, vertical, node_B)
add_fixed_constraint(top_right, bottom_right, node_C) # Joint C
add_fixed_constraint(bottom_left, bottom_right, node_D) # Joint D
add_fixed_constraint(bottom_left, vertical, node_D)
add_fixed_constraint(bottom_right, vertical, node_D)

# Anchor supports to ground
add_fixed_constraint(top_left, ground, node_A)
add_fixed_constraint(bottom_left, ground, node_A)
add_fixed_constraint(top_right, ground, node_C)
add_fixed_constraint(bottom_right, ground, node_C)

# Apply downward forces at top chord nodes (A, B, C)
# Create force field objects at each node
force_nodes = [node_A, node_B, node_C]
for i, node in enumerate(force_nodes):
    bpy.ops.object.empty_add(type='SPHERE', location=node)
    force_empty = bpy.context.active_object
    force_empty.name = f"Force_Node_{i}"
    bpy.ops.object.forcefield_add()
    force_empty.field.type = 'FORCE'
    force_empty.field.strength = -force_per_node  # Downward
    force_empty.field.use_max_distance = True
    force_empty.field.distance_max = 0.5  # Only affect nearby objects

# Ensure rigid body world is enabled
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Set gravity to standard Earth
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)