import bpy
import math
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Set gravity
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.effector_weights.gravity = 1.0

# ========== PARAMETERS ==========
# Main beam
main_len = 4.0
main_w = 0.3
main_h = 0.3
main_z = 1.5
main_center = (2.0, 0.0, 1.5)

# Column
col_w = 0.3
col_d = 0.3
col_h = 1.5
col_center = (0.0, 0.0, 0.75)

# Diagonals
diag_cs = 0.2
diag1_len = 2.5495097568
diag1_center = (1.0, 0.25, 0.75)
diag2_len = 2.5495097568
diag2_center = (1.0, -0.25, 0.75)

# Load
load_mass = 300.0
load_loc = (4.0, 0.0, 1.5)
load_sz = 0.2

# Ground
ground_sz = 10.0
ground_thick = 0.5

# ========== CREATE GROUND ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -ground_thick/2))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (ground_sz, ground_sz, ground_thick)
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# ========== CREATE VERTICAL COLUMN ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_center)
column = bpy.context.active_object
column.name = "Vertical_Column"
column.scale = (col_w/2, col_d/2, col_h/2)  # Default cube is 2x2x2
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.mass = 100.0  # Heavy passive element

# ========== CREATE MAIN BEAM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=main_center)
beam = bpy.context.active_object
beam.name = "Main_Beam"
beam.scale = (main_len/2, main_w/2, main_h/2)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = 50.0  # Mass proportional to volume
beam.rigid_body.use_deactivation = False

# ========== CREATE DIAGONAL BRACE 1 ==========
# Create cube at origin
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
diag1 = bpy.context.active_object
diag1.name = "Diagonal_Brace_1"
# Scale: default cube is 2 units, so divide by 2
diag1.scale = (diag_cs/2, diag_cs/2, diag1_len/2)

# Calculate rotation to align with vector from start to end
start_vec = mathutils.Vector((0, 0, 1.5))
end_vec = mathutils.Vector((2, 0.5, 0))
direction = (end_vec - start_vec).normalized()

# Default cube's local Z axis points up (0,0,1)
default_z = mathutils.Vector((0, 0, 1))
rotation_quat = default_z.rotation_difference(direction)
diag1.rotation_euler = rotation_quat.to_euler()

# Move to center position
diag1.location = diag1_center

# Add rigid body
bpy.ops.rigidbody.object_add()
diag1.rigid_body.type = 'ACTIVE'
diag1.rigid_body.collision_shape = 'BOX'
diag1.rigid_body.mass = 20.0
diag1.rigid_body.use_deactivation = False

# ========== CREATE DIAGONAL BRACE 2 ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
diag2 = bpy.context.active_object
diag2.name = "Diagonal_Brace_2"
diag2.scale = (diag_cs/2, diag_cs/2, diag2_len/2)

# Rotation for second diagonal
start_vec = mathutils.Vector((0, 0, 1.5))
end_vec = mathutils.Vector((2, -0.5, 0))
direction = (end_vec - start_vec).normalized()
rotation_quat = default_z.rotation_difference(direction)
diag2.rotation_euler = rotation_quat.to_euler()

# Move to center position
diag2.location = diag2_center

# Add rigid body
bpy.ops.rigidbody.object_add()
diag2.rigid_body.type = 'ACTIVE'
diag2.rigid_body.collision_shape = 'BOX'
diag2.rigid_body.mass = 20.0
diag2.rigid_body.use_deformation = False

# ========== CREATE LOAD ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load_300kg"
load.scale = (load_sz/2, load_sz/2, load_sz/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass
load.rigid_body.use_deactivation = False

# ========== CREATE CONSTRAINTS ==========
# Function to create fixed constraint between two objects at world location
def create_fixed_constraint(obj1, obj2, world_location, name):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=world_location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    constraint.disable_collisions = True
    
    return constraint_empty

# Constraint 1: Beam to Column at (0,0,1.5)
create_fixed_constraint(beam, column, (0.0, 0.0, 1.5), "Beam_Column_Constraint")

# Constraint 2: Beam to Diagonal 1 at (0,0,1.5)
create_fixed_constraint(beam, diag1, (0.0, 0.0, 1.5), "Beam_Diag1_Constraint")

# Constraint 3: Beam to Diagonal 2 at (0,0,1.5)
create_fixed_constraint(beam, diag2, (0.0, 0.0, 1.5), "Beam_Diag2_Constraint")

# Constraint 4: Diagonal 1 to Ground at (2,0.5,0)
create_fixed_constraint(diag1, ground, (2.0, 0.5, 0.0), "Diag1_Ground_Constraint")

# Constraint 5: Diagonal 2 to Ground at (2,-0.5,0)
create_fixed_constraint(diag2, ground, (2.0, -0.5, 0.0), "Diag2_Ground_Constraint")

# Constraint 6: Load to Beam at (4,0,1.5)
create_fixed_constraint(load, beam, (4.0, 0.0, 1.5), "Load_Beam_Constraint")

# ========== SETUP SCENE ==========
# Set end frame for simulation
bpy.context.scene.frame_end = simulation_frames

print("Cantilever beam with diagonal bracing constructed successfully.")
print(f"300kg load applied at {load_loc}")
print(f"Simulation will run for {simulation_frames} frames")