import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Define variables from parameter summary
beam_length = 4.0
beam_width = 0.5
beam_height = 0.5
beam_mass = 500.0
column_width = 0.5
column_depth = 0.5
column_height = 2.0
column_mass = 100.0
gravity_z = -9.81
ground_size = 10.0

# Calculated positions
beam_center_x = beam_length / 2.0
beam_center_y = column_width / 2.0  # 0.25
beam_center_z = column_height + (beam_height / 2.0)  # 2.25
column_center_x = column_width / 2.0  # 0.25
column_center_y = column_depth / 2.0  # 0.25
column_center_z = column_height / 2.0  # 1.0
column_top_z = column_height  # 2.0
simulation_frames = 100

# Set world gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = mathutils.Vector((0.0, 0.0, gravity_z))

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create vertical support column (active rigid body, fixed via constraint)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(column_center_x, column_center_y, column_center_z))
column = bpy.context.active_object
column.name = "Column"
column.scale = (column_width, column_depth, column_height)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = column_mass
column.rigid_body.collision_shape = 'BOX'

# Create horizontal beam (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(beam_center_x, beam_center_y, beam_center_z))
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_length, beam_width, beam_height)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = beam_mass
beam.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between column base and ground
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(column_center_x, column_center_y, 0))
constraint_base = bpy.context.active_object
constraint_base.name = "Constraint_Base"
bpy.ops.rigidbody.constraint_add()
constraint_base.rigid_body_constraint.type = 'FIXED'
constraint_base.rigid_body_constraint.object1 = ground
constraint_base.rigid_body_constraint.object2 = column

# Create fixed constraint between column top and beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(column_center_x, column_center_y, column_top_z))
constraint_top = bpy.context.active_object
constraint_top.name = "Constraint_Top"
bpy.ops.rigidbody.constraint_add()
constraint_top.rigid_body_constraint.type = 'FIXED'
constraint_top.rigid_body_constraint.object1 = column
constraint_top.rigid_body_constraint.object2 = beam

# Set up simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print(f"Cantilever structure created. Beam mass: {beam_mass} kg, Column mass: {column_mass} kg")
print(f"Simulation running for {simulation_frames} frames")