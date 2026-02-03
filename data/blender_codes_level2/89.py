import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_size = (0.5, 0.5, 2.0)
col_center = (0.25, 0.25, 1.0)
beam_size = (5.0, 0.5, 0.5)
beam_center = (2.5, 0.0, 2.25)
load_size = (0.5, 0.5, 0.5)
load_mass = 600.0
load_loc = (4.75, 0.0, 1.0)
bond_col_beam = (0.25, 0.25, 2.0)
bond_beam_load = (4.75, 0.0, 1.0)

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create vertical support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_center)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_size
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create main horizontal beam
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_center)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_size
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'

# Create load block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_size
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Add fixed constraint between column and ground (world)
# In Blender, a passive rigid body is already fixed to world unless constrained otherwise.
# We need an empty to serve as ground anchor? Actually, we can create a constraint between column and world by making column passive.
# But the task says "bond the vertical support column to the ground at Z=0 using a FIXED constraint".
# We'll create a static ground plane at Z=0 and fix column to it.
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create fixed constraint between ground and column
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Ground_Column_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = ground
constraint.object2 = column

# Create fixed constraint between column and beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=bond_col_beam)
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Column_Beam_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = column
constraint2.object2 = beam

# Create fixed constraint between beam and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=bond_beam_load)
constraint_empty3 = bpy.context.active_object
constraint_empty3.name = "Beam_Load_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint3 = constraint_empty3.rigid_body_constraint
constraint3.type = 'FIXED'
constraint3.object1 = beam
constraint3.object2 = load

# Set simulation end frame to 100 for verification
bpy.context.scene.frame_end = 100