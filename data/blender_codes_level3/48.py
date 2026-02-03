import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 2.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
arm1_dim = (0.2, 2.0, 0.2)
arm1_center = (1.0, 0.0, 0.5)
arm2_dim = (0.2, 1.5, 0.2)
arm2_center = (2.75, 0.0, 0.5)
proj_size = 0.3
proj_loc = (3.5, 0.0, 0.75)
hinge1_pivot = (0.0, 0.0, 0.5)
hinge2_pivot = (2.0, 0.0, 0.5)
motor_velocity = 5.0
sim_frames = 100

# Enable rigid body physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
rigidbody_world = bpy.context.scene.rigidbody_world
if rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
    rigidbody_world = bpy.context.scene.rigidbody_world
rigidbody_world.substeps_per_frame = 10
rigidbody_world.solver_iterations = 10

# Function to create rigid body objects
def create_rigid_body(obj, body_type='ACTIVE', collision_shape='CONVEX_HULL'):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.collision_shape = collision_shape
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.1
    obj.rigid_body.linear_damping = 0.04
    obj.rigid_body.angular_damping = 0.1

# 1. Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
create_rigid_body(base, 'PASSIVE')

# 2. First Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm1_center)
arm1 = bpy.context.active_object
arm1.name = "Arm1"
arm1.scale = arm1_dim
create_rigid_body(arm1, 'ACTIVE')

# 3. Second Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm2_center)
arm2 = bpy.context.active_object
arm2.name = "Arm2"
arm2.scale = arm2_dim
create_rigid_body(arm2, 'ACTIVE')

# 4. Projectile Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=proj_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = (proj_size, proj_size, proj_size)
create_rigid_body(projectile, 'ACTIVE')

# 5. Constraints
# Base-to-World Fixed Constraint (dummy empty as world anchor)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
world_anchor = bpy.context.active_object
world_anchor.name = "World_Anchor"
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Base_Fixed"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = world_anchor
constraint.rigid_body_constraint.object2 = base
constraint.location = base_loc

# Hinge 1: Base to Arm1
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge1_pivot)
hinge1 = bpy.context.active_object
hinge1.name = "Hinge1"
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Constraint1"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = base
constraint.rigid_body_constraint.object2 = arm1
constraint.rigid_body_constraint.use_limit_ang_z = True
constraint.rigid_body_constraint.limit_ang_z_lower = 0.0
constraint.rigid_body_constraint.limit_ang_z_upper = math.radians(120)
constraint.rigid_body_constraint.use_motor_ang = True
constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
constraint.location = hinge1_pivot
constraint.rotation_euler = (0.0, 0.0, 0.0)  # Y-axis hinge

# Hinge 2: Arm1 to Arm2
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge2_pivot)
hinge2 = bpy.context.active_object
hinge2.name = "Hinge2"
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Constraint2"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = arm1
constraint.rigid_body_constraint.object2 = arm2
constraint.rigid_body_constraint.use_limit_ang_z = True
constraint.rigid_body_constraint.limit_ang_z_lower = 0.0
constraint.rigid_body_constraint.limit_ang_z_upper = math.radians(120)
constraint.rigid_body_constraint.use_motor_ang = True
constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
constraint.location = hinge2_pivot
constraint.rotation_euler = (0.0, 0.0, 0.0)

# Initial Fixed Constraint: Arm2 to Projectile (breaks during launch)
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Launch_Constraint"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.rigid_body_constraint.object1 = arm2
constraint.rigid_body_constraint.object2 = projectile
constraint.rigid_body_constraint.breaking_threshold = 50.0  # Weak bond
constraint.location = hinge2_pivot

# Set simulation frames
bpy.context.scene.frame_end = sim_frames

# Bake simulation for headless verification
bpy.ops.ptcache.bake_all(bake=True)
print("Catapult assembly complete. Simulation baked.")