import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
col_dim = (1.0, 1.0, 3.0)
col_loc = (0.0, 0.0, 1.5)  # Column centered at Z=1.5 so top at Z=3
arm_dim = (6.0, 0.5, 0.5)
arm_loc = (3.0, 0.0, 3.0)
load_dim = (0.5, 0.5, 0.5)
load_loc = (6.0, 0.0, 3.0)
load_mass = 350.0
con_loc = (0.0, 0.0, 3.0)
sim_frames = 100

# Create support column (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.scale = col_dim
column.name = "Support_Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create jib arm (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_dim
arm.name = "Jib_Arm"
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.scale = load_dim
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Create fixed constraint between column and arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=con_loc)
constraint = bpy.context.active_object
constraint.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'FIXED'

# Parent constraint to column and set arm as target
constraint.parent = column
constraint.rigid_body_constraint.object1 = column
constraint.rigid_body_constraint.object2 = arm

# Create second fixed constraint between arm and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
constraint2 = bpy.context.active_object
constraint2.name = "Load_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.parent = arm
constraint2.rigid_body_constraint.object1 = arm
constraint2.rigid_body_constraint.object2 = load

# Set up scene for simulation
bpy.context.scene.frame_end = sim_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Ensure proper collision margins
for obj in [column, arm, load]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

# Run simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)