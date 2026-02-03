import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Extract parameters from summary
col_w = 0.3
col_d = 0.3
col_h = 1.5
col_center_z = col_h / 2.0

beam_len = 2.5
beam_w = 0.3
beam_h = 0.3
beam_center_x = beam_len / 2.0
beam_center_z = col_h + (beam_h / 2.0)

cube_sz = 0.5
cube_center_x = beam_len
cube_center_z = beam_center_z + (beam_h / 2.0) + (cube_sz / 2.0)

load_mass = 800.0
sim_frames = 100
gravity = -9.81

# Set world gravity
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = mathutils.Vector((0.0, 0.0, gravity))

# Create Vertical Column (Passive Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, col_center_z))
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_w, col_d, col_h)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create Horizontal Beam (Active Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(beam_center_x, 0.0, beam_center_z))
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_len, beam_w, beam_h)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = 10.0  # Arbitrary beam mass (10 kg)
beam.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraint between Column and Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, col_h))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = column
constraint.object2 = beam

# Create Load Cube (Active Rigid Body with 800 kg)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cube_center_x, 0.0, cube_center_z))
load_cube = bpy.context.active_object
load_cube.name = "Load_Cube"
load_cube.scale = (cube_sz, cube_sz, cube_sz)
bpy.ops.rigidbody.object_add()
load_cube.rigid_body.type = 'ACTIVE'
load_cube.rigid_body.mass = load_mass
load_cube.rigid_body.collision_shape = 'BOX'

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

# Ensure proper collision margins (use default)
for obj in [column, beam, load_cube]:
    obj.rigid_body.use_margin = True
    obj.rigid_body.collision_margin = 0.0  # Default value

# Set rigid body damping to zero for clear observation
beam.rigid_body.linear_damping = 0.0
beam.rigid_body.angular_damping = 0.0
load_cube.rigid_body.linear_damping = 0.0
load_cube.rigid_body.angular_damping = 0.0

# Bake simulation (headless compatible)
bpy.context.scene.frame_set(1)
bpy.ops.ptcache.bake_all(bake=True)