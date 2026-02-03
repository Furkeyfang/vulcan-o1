import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_dim = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.0)
beam_dim = (3.0, 0.5, 0.5)
beam_loc = (1.5, 0.0, 2.25)
load_dim = (0.5, 0.5, 0.5)
load_loc = (3.0, 0.0, 2.75)
load_mass = 500.0
sim_frames = 150
substeps = 10
deflection_thresh = 0.1

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.substeps_per_frame = substeps
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create Column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
col = bpy.context.active_object
col.scale = col_dim
col.name = "Column"
bpy.ops.rigidbody.object_add()
col.rigid_body.type = 'PASSIVE'
col.rigid_body.collision_shape = 'BOX'

# Create Beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.scale = beam_dim
beam.name = "Beam"
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.collision_shape = 'BOX'
beam.rigid_body.mass = beam_dim[0] * beam_dim[1] * beam_dim[2] * 7850  # Steel density kg/m³

# Create Load Block
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.scale = load_dim
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass

# Add Fixed Constraint between Column and Beam
constraint = beam.constraints.new(type='RIGID_BODY_JOINT')
constraint.object1 = col
constraint.object2 = beam
constraint.pivot_type = 'CENTER'
constraint.limit_lin_x = constraint.limit_lin_y = constraint.limit_lin_z = True
constraint.limit_ang_x = constraint.limit_ang_y = constraint.limit_ang_z = True
constraint.use_limit_lin_x = constraint.use_limit_lin_y = constraint.use_limit_lin_z = True
constraint.use_limit_ang_x = constraint.use_limit_ang_y = constraint.use_limit_ang_z = True
for i in range(3):
    constraint.limit_lin_lower[i] = constraint.limit_lin_upper[i] = 0
    constraint.limit_ang_lower[i] = constraint.limit_ang_upper[i] = 0

# Set up simulation and deflection measurement
bpy.context.scene.frame_end = sim_frames
initial_z = beam_loc[2] + beam_dim[2]/2  # Top surface of beam at free end (X=3)
deflection = 0.0

# Run simulation frames
for frame in range(1, sim_frames + 1):
    bpy.context.scene.frame_set(frame)
    # Get free end vertex position (vertex at beam local +X, +Z)
    # Beam local: vertices at ±0.5 in each axis. We want (+0.5, 0, +0.5) in local coords.
    local_pos = mathutils.Vector((0.5, 0.0, 0.5))
    world_pos = beam.matrix_world @ local_pos
    if frame == sim_frames:
        deflection = initial_z - world_pos.z

# Output verification
print(f"Initial beam top at free end: Z = {initial_z:.3f} m")
print(f"Final beam top at free end: Z = {world_pos.z:.3f} m")
print(f"Vertical deflection: {deflection:.3f} m")
print(f"Requirement (< {deflection_thresh} m): {'PASS' if deflection < deflection_thresh else 'FAIL'}")