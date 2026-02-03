import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.1)
base_loc = (0.0, 0.0, 0.0)
arm_dim = (3.0, 0.5, 0.3)
arm_loc = (3.0, 0.0, 0.2)
gen_dim = (1.0, 1.0, 0.05)
gen_loc = (4.0, 0.0, 0.375)
load_mass_kg = 600.0
load_force_newton = 5886.0
constraint_strength = 1000000.0
simulation_frames = 100

# Enable rigid body physics
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'
base.rigid_body.mass = 1000.0  # Heavy base for stability

# Create Cantilever Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "CantileverArm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 500.0  # Substantial mass for stiffness

# Create Generator Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=gen_loc)
gen = bpy.context.active_object
gen.name = "GeneratorPlatform"
gen.scale = gen_dim
bpy.ops.rigidbody.object_add()
gen.rigid_body.type = 'ACTIVE'
gen.rigid_body.collision_shape = 'BOX'
gen.rigid_body.mass = load_mass_kg  # Mass equivalent to load

# Create Fixed Constraint: Base to Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.5, 0.0, 0.2))
constraint_empty1 = bpy.context.active_object
constraint_empty1.name = "BaseArm_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint1 = constraint_empty1.rigid_body_constraint
constraint1.type = 'FIXED'
constraint1.object1 = base
constraint1.object2 = arm
constraint1.use_breaking = True
constraint1.breaking_threshold = constraint_strength

# Create Fixed Constraint: Arm to Generator
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(4.5, 0.0, 0.375))
constraint_empty2 = bpy.context.active_object
constraint_empty2.name = "ArmGen_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2 = constraint_empty2.rigid_body_constraint
constraint2.type = 'FIXED'
constraint2.object1 = arm
constraint2.object2 = gen
constraint2.use_breaking = True
constraint2.breaking_threshold = constraint_strength

# Apply downward force to generator platform
# In Blender, forces are applied via force fields or directly to rigid body
# We'll use a constant force field directed downward
bpy.ops.object.empty_add(type='PLAIN_AXES', location=gen_loc)
force_field = bpy.context.active_object
force_field.name = "LoadForce"
bpy.ops.object.forcefield_add()
force_field.field.type = 'FORCE'
force_field.field.strength = -load_force_newton  # Negative Z direction
force_field.field.use_gravity_falloff = False
force_field.field.distance_max = 0.01  # Very small to affect only generator

# Parent force field to generator so it moves with it
force_field.parent = gen
force_field.matrix_parent_inverse = gen.matrix_world.inverted()

# Set simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.enabled = True

# Bake simulation for headless execution
bpy.ops.ptcache.bake_all(bake=True)