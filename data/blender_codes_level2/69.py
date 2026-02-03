import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
board_dim = (4.0, 0.5, 0.2)
board_loc = (2.0, 0.0, 2.1)
column_dim = (0.5, 0.5, 2.0)
column_loc = (0.0, 0.0, 1.0)
cube_dim = (0.3, 0.3, 0.3)
cube_loc = (4.0, 0.0, 2.35)
material_density = 1000.0
cube_mass = 80.0
cube_volume = cube_dim[0] * cube_dim[1] * cube_dim[2]
cube_density = cube_mass / cube_volume

# Create support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.scale = column_dim
column.name = "Support_Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.mass = material_density * (column_dim[0] * column_dim[1] * column_dim[2])

# Create diving board
bpy.ops.mesh.primitive_cube_add(size=1.0, location=board_loc)
board = bpy.context.active_object
board.scale = board_dim
board.name = "Diving_Board"
bpy.ops.rigidbody.object_add()
board.rigid_body.type = 'ACTIVE'
board.rigid_body.mass = material_density * (board_dim[0] * board_dim[1] * board_dim[2])

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_loc)
cube = bpy.context.active_object
cube.scale = cube_dim
cube.name = "Load_Cube"
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.mass = cube_mass
cube.rigid_body.use_mass = True  # Override density with direct mass

# Add fixed constraint between board and column
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 2.0))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Board_Column_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = column
constraint.object2 = board

# Add fixed constraint between cube and board
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(4.0, 0.0, 2.35))
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Cube_Board_Fixed"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = board
constraint2.object2 = cube

# Set world physics
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Setup collision margins
for obj in [column, board, cube]:
    obj.rigid_body.collision_margin = 0.001
    obj.rigid_body.use_margin = True

print("Diving board structure created. Run simulation to measure tip deflection.")