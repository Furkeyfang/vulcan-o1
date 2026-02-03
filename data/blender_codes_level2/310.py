import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
tower_dim = (2.0, 2.0, 18.0)
tower_loc = (0.0, 0.0, 9.0)

platform_dim = (3.0, 3.0, 0.5)
platform_offset_x = 2.5
platform_loc = (2.5, 0.0, 18.25)

counter_dim = (1.0, 1.0, 2.0)
counter_loc = (-2.5, 0.0, 19.5)
counter_mass = 1633.33

load_dim = (1.0, 1.0, 1.0)
load_loc = (4.5, 0.0, 19.0)
load_mass = 700.0

hinge_pivot = (0.0, 0.0, 18.25)
hinge_axis = (0.0, 0.0, 1.0)
hinge_limit_lower = 0.0
hinge_limit_upper = 0.436332  # 25° in radians
hinge_friction = 0.1

# Create Tower Base (Passive/Static)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=tower_loc)
tower = bpy.context.active_object
tower.name = "Tower_Base"
tower.scale = tower_dim
bpy.ops.rigidbody.object_add()
tower.rigid_body.type = 'PASSIVE'
tower.rigid_body.collision_shape = 'MESH'

# Create Rotating Platform (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Rotating_Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'MESH'
platform.rigid_body.mass = 100.0  # Platform mass

# Create Counterweight (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=counter_loc)
counter = bpy.context.active_object
counter.name = "Counterweight"
counter.scale = counter_dim
bpy.ops.rigidbody.object_add()
counter.rigid_body.type = 'ACTIVE'
counter.rigid_body.collision_shape = 'MESH'
counter.rigid_body.mass = counter_mass

# Create Load Block (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load_Block"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'MESH'
load.rigid_body.mass = load_mass

# Create Hinge Constraint between Tower and Platform
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge_empty.rigid_body_constraint.type = 'HINGE'
hinge_empty.rigid_body_constraint.object1 = tower
hinge_empty.rigid_body_constraint.object2 = platform
hinge_empty.rigid_body_constraint.use_limit_ang_z = True
hinge_empty.rigid_body_constraint.limit_ang_z_lower = hinge_limit_lower
hinge_empty.rigid_body_constraint.limit_ang_z_upper = hinge_limit_upper
hinge_empty.rigid_body_constraint.use_motor_ang = False
hinge_empty.rigid_body_constraint.use_friction = True
hinge_empty.rigid_body_constraint.friction = hinge_friction

# Create Fixed Constraint between Platform and Counterweight
bpy.ops.object.empty_add(type='PLAIN_AXES', location=counter_loc)
fixed_counter = bpy.context.active_object
fixed_counter.name = "Fixed_Counterweight"
bpy.ops.rigidbody.constraint_add()
fixed_counter.rigid_body_constraint.type = 'FIXED'
fixed_counter.rigid_body_constraint.object1 = platform
fixed_counter.rigid_body_constraint.object2 = counter

# Create Fixed Constraint between Platform and Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
fixed_load = bpy.context.active_object
fixed_load.name = "Fixed_Load"
bpy.ops.rigidbody.constraint_add()
fixed_load.rigid_body_constraint.type = 'FIXED'
fixed_load.rigid_body_constraint.object1 = platform
fixed_load.rigid_body_constraint.object2 = load

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Crane assembly complete. Tower fixed, platform rotates 0-25°, load (700kg) secured.")