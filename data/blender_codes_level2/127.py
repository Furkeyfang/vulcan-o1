import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
col_sz = (0.5, 0.5, 2.0)
col_loc = (0.0, 0.0, 1.0)
arm_sz = (5.0, 0.5, 0.5)
arm_loc = (2.5, 0.0, 2.0)
load_mass = 750.0
load_sz = (0.5, 0.5, 0.5)
load_loc = (5.0, 0.0, 2.0)
ground_sz = (10.0, 10.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)

# Create ground plane (static foundation)
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_sz
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create vertical column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = col_sz
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.mass = 100.0  # reasonable mass for steel column
column.rigid_body.collision_shape = 'BOX'

# Create horizontal arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_sz
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = 50.0  # steel arm mass estimate
arm.rigid_body.collision_shape = 'BOX'

# Create load block
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_sz
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between ground and column base
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
constraint1 = bpy.context.active_object
constraint1.name = "Ground_Column_Fixed"
bpy.ops.rigidbody.constraint_add()
rb_constraint1 = constraint1.rigid_body_constraint
rb_constraint1.type = 'FIXED'
rb_constraint1.object1 = ground
rb_constraint1.object2 = column

# Create fixed constraint between column top and arm left end
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,2))
constraint2 = bpy.context.active_object
constraint2.name = "Column_Arm_Fixed"
bpy.ops.rigidbody.constraint_add()
rb_constraint2 = constraint2.rigid_body_constraint
rb_constraint2.type = 'FIXED'
rb_constraint2.object1 = column
rb_constraint2.object2 = arm

# Create fixed constraint between arm right end and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(5,0,2))
constraint3 = bpy.context.active_object
constraint3.name = "Arm_Load_Fixed"
bpy.ops.rigidbody.constraint_add()
rb_constraint3 = constraint3.rigid_body_constraint
rb_constraint3.type = 'FIXED'
rb_constraint3.object1 = arm
rb_constraint3.object2 = load

# Set up rigid body world for simulation
scene = bpy.context.scene
scene.rigidbody_world.enabled = True
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50
scene.rigidbody_world.use_split_impulse = True

print("Cantilever gantry arm constructed with 750 kg load.")