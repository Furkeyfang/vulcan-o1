import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
column_dim = (0.5, 0.5, 4.0)
column_loc = (0.0, 0.0, 2.5)
boom_dim = (4.0, 0.5, 0.5)
boom_loc = (2.0, 0.0, 4.75)
load_radius = 0.3
load_height = 0.5
load_loc = (4.0, 0.0, 4.75)
hinge_pivot = (0.0, 0.0, 4.5)
motor_velocity = 2.0
simulation_frames = 100
fps = 60

# Set scene physics properties
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.render.fps = fps
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create support column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Fixed constraint: Base to Column
bpy.ops.object.empty_add(type='PLAIN_AXES', location=column_loc)
empty_fixed = bpy.context.active_object
empty_fixed.name = "Fixed_Base_Column"
bpy.ops.rigidbody.constraint_add()
constraint = empty_fixed.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = base
constraint.object2 = column

# Create boom arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=boom_loc)
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.collision_shape = 'BOX'

# Hinge constraint: Column to Boom
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
empty_hinge = bpy.context.active_object
empty_hinge.name = "Hinge_Column_Boom"
bpy.ops.rigidbody.constraint_add()
hinge = empty_hinge.rigid_body_constraint
hinge.type = 'HINGE'
hinge.object1 = column
hinge.object2 = boom
hinge.use_limit_ang_z = False
hinge.use_motor_ang = True
hinge.motor_ang_target_velocity = motor_velocity
hinge.motor_ang_max_impulse = 100.0  # Sufficient torque

# Create load cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=load_radius,
    depth=load_height,
    location=load_loc
)
load = bpy.context.active_object
load.name = "Load"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'CYLINDER'

# Fixed constraint: Boom to Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
empty_load = bpy.context.active_object
empty_load.name = "Fixed_Boom_Load"
bpy.ops.rigidbody.constraint_add()
constraint_load = empty_load.rigid_body_constraint
constraint_load.type = 'FIXED'
constraint_load.object1 = boom
constraint_load.object2 = load

# Set collision margins (headless compatible)
for obj in [base, column, boom, load]:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.04

print("Crane assembly complete. Motor set to", motor_velocity, "rad/s.")
print("Expected horizontal displacement after", simulation_frames, "frames:", 
      round(4 * abs(1 - math.cos(motor_velocity * simulation_frames / fps)), 2), "meters")