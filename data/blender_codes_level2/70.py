import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
col_dim = (0.5, 0.5, 10.0)
col_loc = (0.0, 0.0, 5.0005)  # Slightly above ground
beam_dim = (2.0, 0.5, 0.5)
beam_loc = (1.0, 0.0, 10.0)
load_force = 1962.0  # Newtons (200 kg * 9.81)
load_point = (2.0, 0.0, 10.0)
ground_size = (20.0, 20.0, 0.2)
ground_loc = (0.0, 0.0, 0.0)

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.scale = ground_size
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create vertical column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.scale = col_dim
column.name = "Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = 100.0  # kg (stiff structure)
column.rigid_body.collision_shape = 'BOX'

# Create overhang beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.scale = beam_dim
beam.name = "Beam"
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = 50.0  # kg
beam.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between ground and column
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint1 = bpy.context.active_object
constraint1.name = "Ground_Column_Fixed"
constraint1.rigid_body_constraint.object1 = ground
constraint1.rigid_body_constraint.object2 = column
constraint1.location = (0, 0, 0.001)  # At base of column

# Create fixed constraint between column and beam
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint2 = bpy.context.active_object
constraint2.name = "Column_Beam_Fixed"
constraint2.rigid_body_constraint.object1 = column
constraint2.rigid_body_constraint.object2 = beam
constraint2.location = (0, 0, 10.0)  # Connection point at column top

# Apply downward force at beam end using force field
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_point)
force_empty = bpy.context.active_object
force_empty.name = "Load_Force"
bpy.ops.object.forcefield_add()
force_empty.field.type = 'FORCE'
force_empty.field.strength = -load_force  # Negative for downward
force_empty.field.use_max_distance = True
force_empty.field.distance_max = 0.5  # Only affect nearby objects
force_empty.field.falloff_power = 0  # Constant force within range

# Limit force field to affect only the beam
beam.rigid_body.use_deactivation = False
beam.rigid_body.linear_damping = 0.5  # Reduce oscillation
beam.rigid_body.angular_damping = 0.5

# Set up rigid body world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 100  # Simulate 100 frames

# Optional: Add visual materials for clarity
mat_col = bpy.data.materials.new(name="Column_Mat")
mat_col.diffuse_color = (0.1, 0.3, 0.8, 1.0)  # Blue
column.data.materials.append(mat_col)

mat_beam = bpy.data.materials.new(name="Beam_Mat")
mat_beam.diffuse_color = (0.8, 0.2, 0.1, 1.0)  # Red
beam.data.materials.append(mat_beam)

print("Billboard support frame constructed. Run simulation with rigid body solver.")