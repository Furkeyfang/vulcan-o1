import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
ground_size = 10.0
column_dim = (0.3, 0.3, 1.0)
column_loc = (0.0, 0.0, 0.5)
pipe_radius = 0.1
pipe_length = 2.0
pipe_loc = (1.0, 0.0, 1.0)
force_magnitude = 1961.33
force_location = (2.0, 0.0, 1.0)
connection_column_top = (0.0, 0.0, 1.0)
connection_ground = (0.0, 0.0, 0.0)
steel_density = 7850.0
simulation_frames = 100
deflection_limit = 0.05
solver_iterations = 50

# Enable rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

# Create column (cube)
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (column_dim[0], column_dim[1], column_dim[2])
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.collision_shape = 'MESH'
column.rigid_body.mass = steel_density * (column_dim[0] * column_dim[1] * column_dim[2])

# Create pipe (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=pipe_radius,
    depth=pipe_length,
    location=pipe_loc,
    rotation=(0, math.pi/2, 0)
)
pipe = bpy.context.active_object
pipe.name = "Pipe"
bpy.ops.rigidbody.object_add()
pipe.rigid_body.type = 'ACTIVE'
pipe.rigid_body.collision_shape = 'MESH'
pipe_volume = math.pi * pipe_radius**2 * pipe_length
pipe.rigid_body.mass = steel_density * pipe_volume

# Create fixed constraint between ground and column
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint1 = bpy.context.active_object
constraint1.name = "Ground_Column_Fixed"
constraint1.location = connection_ground
constraint1.rigid_body_constraint.object1 = ground
constraint1.rigid_body_constraint.object2 = column
constraint1.rigid_body_constraint.disable_collisions = True

# Create fixed constraint between column and pipe
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint2 = bpy.context.active_object
constraint2.name = "Column_Pipe_Fixed"
constraint2.location = connection_column_top
constraint2.rigid_body_constraint.object1 = column
constraint2.rigid_body_constraint.object2 = pipe
constraint2.rigid_body_constraint.disable_collisions = True

# Create force application constraint at free end
bpy.ops.rigidbody.constraint_add(type='MOTOR')
force_constraint = bpy.context.active_object
force_constraint.name = "Load_Force"
force_constraint.location = force_location
force_constraint.rigid_body_constraint.object1 = pipe
force_constraint.rigid_body_constraint.object2 = None  # Applies to world
force_constraint.rigid_body_constraint.motor_lin_target_velocity = 0.0
force_constraint.rigid_body_constraint.use_motor_lin = True
force_constraint.rigid_body_constraint.motor_lin_force = force_magnitude
force_constraint.rigid_body_constraint.motor_lin_direction = (0, 0, -1)  # Downward

# Bake simulation for verification
bpy.context.scene.frame_end = simulation_frames
bpy.ops.ptcache.bake_all(bake=True)

# Print deflection information
pipe_z_initial = pipe_loc[2]
pipe_z_final = pipe.matrix_world.translation.z
deflection = pipe_z_initial - pipe_z_final
print(f"Initial pipe Z: {pipe_z_initial:.4f}m")
print(f"Final pipe Z at frame {simulation_frames}: {pipe_z_final:.4f}m")
print(f"Vertical deflection: {abs(deflection):.4f}m")
print(f"Deflection limit: {deflection_limit}m")
print(f"Requirement met: {abs(deflection) < deflection_limit}")