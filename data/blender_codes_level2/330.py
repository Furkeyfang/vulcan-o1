import bpy
import math
from mathutils import Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
base_dim = (18.0, 6.0, 2.0)
base_loc = (0.0, 0.0, 1.0)
cantilever_dim = (2.0, 2.0, 12.0)
cantilever_loc = (-8.0, 0.0, 8.0)
crossbeam_dim = (4.0, 0.5, 0.5)
crossbeam_loc = (-8.0, 0.0, 14.0)
brace_dim = (1.0, 1.0, 10.0)
brace_scale = 0.481
brace_mid = (0.5, 0.0, 8.0)
brace_rot = 2.529  # 145° in radians
load_mass = 1500.0
load_loc = (-8.0, 0.0, 14.0)
load_dim = (0.5, 0.5, 0.5)
sim_frames = 500

# Enable rigid body physics
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 1. BASE FRAME
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "BaseFrame"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. CANTILEVER BEAM
bpy.ops.mesh.primitive_cube_add(size=1, location=cantilever_loc)
cantilever = bpy.context.active_object
cantilever.name = "Cantilever"
cantilever.scale = cantilever_dim
bpy.ops.rigidbody.object_add()
cantilever.rigid_body.type = 'PASSIVE'
cantilever.rigid_body.collision_shape = 'BOX'

# 3. SUSPENSION CROSSBEAM
bpy.ops.mesh.primitive_cube_add(size=1, location=crossbeam_loc)
crossbeam = bpy.context.active_object
crossbeam.name = "Crossbeam"
crossbeam.scale = crossbeam_dim
bpy.ops.rigidbody.object_add()
crossbeam.rigid_body.type = 'ACTIVE'
crossbeam.rigid_body.mass = 50.0  # Estimated 50kg for steel beam
crossbeam.rigid_body.collision_shape = 'BOX'

# 4. DIAGONAL BRACE
bpy.ops.mesh.primitive_cube_add(size=1, location=brace_mid)
brace = bpy.context.active_object
brace.name = "DiagonalBrace"
brace.scale = (brace_dim[0], brace_dim[1], brace_dim[2] * brace_scale)
brace.rotation_euler = (0, brace_rot, 0)
bpy.ops.rigidbody.object_add()
brace.rigid_body.type = 'PASSIVE'
brace.rigid_body.collision_shape = 'BOX'

# 5. LOAD MASS
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "LoadMass"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# CONSTRAINTS
# Fixed: Base to Cantilever
bpy.ops.rigidbody.constraint_add()
constraint1 = bpy.context.active_object
constraint1.name = "Fix_Base_Cantilever"
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = base
constraint1.rigid_body_constraint.object2 = cantilever

# Fixed: Cantilever to Brace
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.name = "Fix_Cantilever_Brace"
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = cantilever
constraint2.rigid_body_constraint.object2 = brace

# Fixed: Brace to Base
bpy.ops.rigidbody.constraint_add()
constraint3 = bpy.context.active_object
constraint3.name = "Fix_Brace_Base"
constraint3.rigid_body_constraint.type = 'FIXED'
constraint3.rigid_body_constraint.object1 = brace
constraint3.rigid_body_constraint.object2 = base

# Hinge: Cantilever to Crossbeam
bpy.ops.rigidbody.constraint_add()
constraint4 = bpy.context.active_object
constraint4.name = "Hinge_Cantilever_Crossbeam"
constraint4.rigid_body_constraint.type = 'HINGE'
constraint4.rigid_body_constraint.object1 = cantilever
constraint4.rigid_body_constraint.object2 = crossbeam
constraint4.rigid_body_constraint.use_limit_ang_z = True
constraint4.rigid_body_constraint.limit_ang_z_lower = -0.35  # ~20° limit
constraint4.rigid_body_constraint.limit_ang_z_upper = 0.35

# Fixed: Crossbeam to Load
bpy.ops.rigidbody.constraint_add()
constraint5 = bpy.context.active_object
constraint5.name = "Fix_Crossbeam_Load"
constraint5.rigid_body_constraint.type = 'FIXED'
constraint5.rigid_body_constraint.object1 = crossbeam
constraint5.rigid_body_constraint.object2 = load

# Position constraints at joint locations
constraint1.location = cantilever_loc
constraint4.location = crossbeam_loc
constraint5.location = load_loc

# Position brace constraints at connection points
constraint2.location = (cantilever_loc[0], 0, cantilever_loc[2] + cantilever_dim[2]/2)
constraint3.location = (base_loc[0] + base_dim[0]/2, 0, base_loc[2] + base_dim[2]/2)

# Set simulation length
bpy.context.scene.frame_end = sim_frames

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

print("Composite structure built with rigid body physics and constraints.")