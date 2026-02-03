import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from parameter_summary
base_dim = (3.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.15)
col_dim = (0.3, 0.3, 2.0)
col_loc = (0.0, 0.0, 1.3)
arm_dim = (4.0, 0.2, 0.2)
arm_pivot = (0.0, 0.0, 2.3)
bucket_dim = (0.5, 0.5, 0.3)
bucket_offset = (2.25, 0.0, 0.25)
cw_dim = (0.8, 0.8, 0.8)
cw_offset = (-2.0, 0.0, 0.5)
proj_rad = 0.2
proj_loc = (2.25, 0.0, 2.55)
hinge_axis = (0.0, 1.0, 0.0)
motor_vel = 5.0

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create support column
bpy.ops.mesh.primitive_cube_add(size=1, location=col_loc)
column = bpy.context.active_object
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'

# Create throwing arm assembly
# Start with arm at pivot point
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_pivot)
arm = bpy.context.active_object
arm.scale = arm_dim

# Create bucket relative to arm pivot
bucket_loc = (
    arm_pivot[0] + bucket_offset[0],
    arm_pivot[1] + bucket_offset[1],
    arm_pivot[2] + bucket_offset[2]
)
bpy.ops.mesh.primitive_cube_add(size=1, location=bucket_loc)
bucket = bpy.context.active_object
bucket.scale = bucket_dim

# Create counterweight relative to arm pivot
cw_loc = (
    arm_pivot[0] + cw_offset[0],
    arm_pivot[1] + cw_offset[1],
    arm_pivot[2] + cw_offset[2]
)
bpy.ops.mesh.primitive_cube_add(size=1, location=cw_loc)
counterweight = bpy.context.active_object
counterweight.scale = cw_dim

# Select all arm components and join
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bucket.select_set(True)
counterweight.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.join()

# Add rigid body to arm assembly
bpy.ops.rigidbody.object_add()
arm.rigid_body.mass = 50.0  # Reasonable mass for arm assembly

# Create projectile sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=proj_rad, location=proj_loc)
projectile = bpy.context.active_object
bpy.ops.rigidbody.object_add()
projectile.rigid_body.mass = 2.0  # Light projectile

# Create fixed constraint between base and column
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
column.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.constraint_add()
constraint_fixed = column.rigid_body_constraint
constraint_fixed.type = 'FIXED'
constraint_fixed.object1 = base

# Create hinge constraint between column and arm
bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.constraint_add()
constraint_hinge = column.rigid_body_constraint
constraint_hinge.type = 'HINGE'
constraint_hinge.object1 = arm
constraint_hinge.pivot_type = 'CUSTOM'
constraint_hinge.pivot_x = arm_pivot[0]
constraint_hinge.pivot_y = arm_pivot[1]
constraint_hinge.pivot_z = arm_pivot[2]
constraint_hinge.use_limit_z = False  # Free rotation
constraint_hinge.use_motor = True
constraint_hinge.motor_velocity = motor_vel
constraint_hinge.motor_max_torque = 1000.0  # High torque for rapid acceleration

# Set up simulation parameters
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.steps_per_second = 250
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 300  # 10 seconds at 30fps

# Ensure collision detection
arm.rigid_body.collision_shape = 'MESH'
projectile.rigid_body.collision_shape = 'SPHERE'