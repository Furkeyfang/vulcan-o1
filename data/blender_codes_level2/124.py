import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
support_dim = (0.5, 0.5, 1.0)
support_loc = (0.0, 0.0, 0.5)
beam_dim = (2.0, 0.2, 0.2)
beam_loc = (1.0, 0.0, 1.0)
load_dim = (0.1, 0.1, 0.1)
load_loc = (2.0, 0.0, 0.85)
load_mass = 80.0
beam_mass = 1.0
gravity_z = -9.8

# Set world gravity
bpy.context.scene.gravity = mathutils.Vector((0, 0, gravity_z))

# 1. Create vertical support (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=support_loc)
support = bpy.context.active_object
support.name = "Support"
support.scale = (support_dim[0]/2, support_dim[1]/2, support_dim[2]/2)  # default cube is 2x2x2
bpy.ops.rigidbody.object_add()
support.rigid_body.type = 'PASSIVE'
support.rigid_body.collision_shape = 'BOX'

# 2. Create horizontal beam (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = (beam_dim[0]/2, beam_dim[1]/2, beam_dim[2]/2)
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'ACTIVE'
beam.rigid_body.mass = beam_mass
beam.rigid_body.collision_shape = 'BOX'

# 3. Create load mass (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_dim[0]/2, load_dim[1]/2, load_dim[2]/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# 4. Create Fixed Constraint between Support and Beam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 1))
constraint_empty = bpy.context.active_object
constraint_empty.name = "Constraint_Support_Beam"
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = support
constraint.object2 = beam

# 5. Create Fixed Constraint between Beam and Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "Constraint_Beam_Load"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = beam
constraint2.object2 = load

# Optional: Set simulation substeps for stability
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Cantilever structure created. Run simulation to verify stability.")