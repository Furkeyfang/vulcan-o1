import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Extract parameters
col_dim = (0.5, 0.5, 6.0)
col_loc = (0.0, 0.0, 3.0)
beam_dim = (2.5, 0.3, 0.3)
beam_loc = (1.25, 0.0, 6.0)
plate_dim = (1.0, 1.0, 0.1)
plate_loc = (2.5, 0.0, 5.8)
plate_mass = 250.0
steel_density = 7850.0
total_frames = 100
gravity = 9.81

# Compute derived masses (volume * density)
beam_vol = beam_dim[0] * beam_dim[1] * beam_dim[2]
beam_mass = beam_vol * steel_density
col_vol = col_dim[0] * col_dim[1] * col_dim[2]
col_mass = col_vol * steel_density

# Create vertical support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_dim[0], col_dim[1], col_dim[2])
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.mass = col_mass
column.rigid_body.collision_shape = 'BOX'

# Create horizontal cantilever beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_dim[0], beam_dim[1], beam_dim[2])
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = beam_mass
beam.rigid_body.collision_shape = 'BOX'

# Create load plate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=plate_loc)
plate = bpy.context.active_object
plate.name = "LoadPlate"
plate.scale = (plate_dim[0], plate_dim[1], plate_dim[2])
bpy.ops.rigidbody.object_add()
plate.rigid_body.type = 'ACTIVE'
plate.rigid_body.mass = plate_mass
plate.rigid_body.collision_shape = 'BOX'

# Set world gravity (Z-down)
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity[2] = -gravity

# Create fixed constraint between column and beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 6.0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Col_Beam_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = column
constraint.object2 = beam

# Create fixed constraint between beam and plate
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(2.5, 0.0, 5.95))
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Beam_Plate_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = beam
constraint2.object2 = plate

# Increase physics accuracy for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set timeline for 100-frame verification
bpy.context.scene.frame_end = total_frames