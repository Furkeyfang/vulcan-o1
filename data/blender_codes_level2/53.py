import bpy
import math
from mathutils import Vector, Matrix

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter summary
vert_beam_size = (0.2, 0.2, 6.0)
horiz_beam_size = (0.2, 0.2, 4.0)
diag_beam_size = (0.2, 0.2, 5.0)
load_size = (1.0, 1.0, 1.0)

side_length = 4.0
triangle_height = 3.464

vert_A_base = (0.0, 0.0, 0.0)
vert_B_base = (side_length, 0.0, 0.0)
vert_C_base = (side_length/2, triangle_height, 0.0)

vert_A_top = (0.0, 0.0, vert_beam_size[2])
vert_B_top = (side_length, 0.0, vert_beam_size[2])
vert_C_top = (side_length/2, triangle_height, vert_beam_size[2])

mid_Z = vert_beam_size[2] / 2
vert_A_mid = (0.0, 0.0, mid_Z)
vert_B_mid = (side_length, 0.0, mid_Z)
vert_C_mid = (side_length/2, triangle_height, mid_Z)

load_pos = (2.0, 1.732, vert_beam_size[2])
load_mass = 500.0

# Function to create a beam with physics
def create_beam(name, location, rotation, scale, rigidbody_type='PASSIVE'):
    """Create a beam primitive with rigid body physics"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    beam = bpy.context.active_object
    beam.name = name
    beam.scale = scale
    
    # Apply rotation
    beam.rotation_euler = rotation
    
    # Apply scale and rotation to mesh
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    beam.rigid_body.type = rigidbody_type
    beam.rigid_body.collision_shape = 'BOX'
    
    return beam

# Function to create fixed constraint between two objects
def create_fixed_constraint(name, obj1, obj2, location):
    """Create a fixed rigid body constraint between two objects"""
    # Create empty at joint location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link the two objects
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    return empty

# Create vertical support beams
print("Creating vertical beams...")
vert_A = create_beam("Vertical_Beam_A", vert_A_base, (0, 0, 0), vert_beam_size)
vert_B = create_beam("Vertical_Beam_B", vert_B_base, (0, 0, 0), vert_beam_size)
vert_C = create_beam("Vertical_Beam_C", vert_C_base, (0, 0, 0), vert_beam_size)

# Create horizontal cross-bracing at top
print("Creating horizontal bracing...")

# Beam AB: between A_top and B_top
ab_center = Vector(vert_A_top) + (Vector(vert_B_top) - Vector(vert_A_top)) / 2
ab_direction = Vector(vert_B_top) - Vector(vert_A_top)
ab_length = ab_direction.length
ab_rotation = Vector((0, 0, 1)).rotation_difference(ab_direction.normalized()).to_euler()

# Scale the beam to fit between vertices (account for beam thickness)
beam_scale = list(horiz_beam_size)
beam_scale[2] = ab_length  # Set length to actual distance
horiz_AB = create_beam("Horizontal_AB", ab_center, ab_rotation, beam_scale)

# Beam BC
bc_center = Vector(vert_B_top) + (Vector(vert_C_top) - Vector(vert_B_top)) / 2
bc_direction = Vector(vert_C_top) - Vector(vert_B_top)
bc_length = bc_direction.length
bc_rotation = Vector((0, 0, 1)).rotation_difference(bc_direction.normalized()).to_euler()
beam_scale[2] = bc_length
horiz_BC = create_beam("Horizontal_BC", bc_center, bc_rotation, beam_scale)

# Beam CA
ca_center = Vector(vert_C_top) + (Vector(vert_A_top) - Vector(vert_C_top)) / 2
ca_direction = Vector(vert_A_top) - Vector(vert_C_top)
ca_length = ca_direction.length
ca_rotation = Vector((0, 0, 1)).rotation_difference(ca_direction.normalized()).to_euler()
beam_scale[2] = ca_length
horiz_CA = create_beam("Horizontal_CA", ca_center, ca_rotation, beam_scale)

# Create diagonal bracing at mid-height
print("Creating diagonal bracing...")

# Diagonal between A_mid and B_mid
diag_AB_center = Vector(vert_A_mid) + (Vector(vert_B_mid) - Vector(vert_A_mid)) / 2
diag_AB_dir = Vector(vert_B_mid) - Vector(vert_A_mid)
diag_AB_length = diag_AB_dir.length
diag_AB_rot = Vector((0, 0, 1)).rotation_difference(diag_AB_dir.normalized()).to_euler()
beam_scale = list(diag_beam_size)
beam_scale[2] = diag_AB_length  # Scale to actual distance
diag_AB = create_beam("Diagonal_AB", diag_AB_center, diag_AB_rot, beam_scale)

# Diagonal between B_mid and C_mid
diag_BC_center = Vector(vert_B_mid) + (Vector(vert_C_mid) - Vector(vert_B_mid)) / 2
diag_BC_dir = Vector(vert_C_mid) - Vector(vert_B_mid)
diag_BC_length = diag_BC_dir.length
diag_BC_rot = Vector((0, 0, 1)).rotation_difference(diag_BC_dir.normalized()).to_euler()
beam_scale[2] = diag_BC_length
diag_BC = create_beam("Diagonal_BC", diag_BC_center, diag_BC_rot, beam_scale)

# Diagonal between C_mid and A_mid
diag_CA_center = Vector(vert_C_mid) + (Vector(vert_A_mid) - Vector(vert_C_mid)) / 2
diag_CA_dir = Vector(vert_A_mid) - Vector(vert_C_mid)
diag_CA_length = diag_CA_dir.length
diag_CA_rot = Vector((0, 0, 1)).rotation_difference(diag_CA_dir.normalized()).to_euler()
beam_scale[2] = diag_CA_length
diag_CA = create_beam("Diagonal_CA", diag_CA_center, diag_CA_rot, beam_scale)

# Create fixed constraints at all joints
print("Creating fixed joints...")

# Top joints (vertical to horizontal)
create_fixed_constraint("Joint_A_top", vert_A, horiz_AB, vert_A_top)
create_fixed_constraint("Joint_B_top_AB", vert_B, horiz_AB, vert_B_top)
create_fixed_constraint("Joint_B_top_BC", vert_B, horiz_BC, vert_B_top)
create_fixed_constraint("Joint_C_top_BC", vert_C, horiz_BC, vert_C_top)
create_fixed_constraint("Joint_C_top_CA", vert_C, horiz_CA, vert_C_top)
create_fixed_constraint("Joint_A_top_CA", vert_A, horiz_CA, vert_A_top)

# Mid-height joints (vertical to diagonal)
create_fixed_constraint("Joint_A_mid_AB", vert_A, diag_AB, vert_A_mid)
create_fixed_constraint("Joint_B_mid_AB", vert_B, diag_AB, vert_B_mid)
create_fixed_constraint("Joint_B_mid_BC", vert_B, diag_BC, vert_B_mid)
create_fixed_constraint("Joint_C_mid_BC", vert_C, diag_BC, vert_C_mid)
create_fixed_constraint("Joint_C_mid_CA", vert_C, diag_CA, vert_C_mid)
create_fixed_constraint("Joint_A_mid_CA", vert_A, diag_CA, vert_A_mid)

# Also connect horizontal beams at corners (triangle vertices)
create_fixed_constraint("Joint_AB_BC", horiz_AB, horiz_BC, vert_B_top)
create_fixed_constraint("Joint_BC_CA", horiz_BC, horiz_CA, vert_C_top)
create_fixed_constraint("Joint_CA_AB", horiz_CA, horiz_AB, vert_A_top)

# Create 500kg load at top center
print("Creating load mass...")
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_pos)
load = bpy.context.active_object
load.name = "Load_Mass"
load.scale = load_size
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add rigid body with mass
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.gravity = (0, 0, -9.8)

# Set simulation frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

print("Truss structure creation complete. Ready for simulation.")