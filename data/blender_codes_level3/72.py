import bpy
import mathutils

# 1. Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define variables from parameter summary
base_dim = (2.0, 2.0, 0.3)
base_loc_z = 0.15
arm_dim = (0.2, 0.2, 1.5)
arm_loc_z = 0.9
proj_size = 0.3
proj_loc_z = 1.8
proj_offset_x = -0.1
hinge_pivot_z = 0.15
hinge_axis = (0.0, 1.0, 0.0)
arm_mass = 5.0
proj_mass = 1.0
motor_vel = 0.0
release_frame = 10
sim_frames = 100

# 3. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, base_loc_z))
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 4. Create Launch Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, arm_loc_z))
arm = bpy.context.active_object
arm.name = "Launch_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass
arm.rigid_body.collision_shape = 'BOX'

# 5. Create Hinge Constraint between Base and Arm
# First, select base then arm (arm becomes active)
base.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Constraint"
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = base
constraint.rigid_body_constraint.object2 = arm
constraint.rigid_body_constraint.pivot_type = 'GENERIC'
constraint.location = (0.0, 0.0, hinge_pivot_z)
constraint.rigid_body_constraint.use_limit_ang_z = False
# Motor setup
constraint.rigid_body_constraint.use_motor_ang = True
constraint.rigid_body_constraint.motor_ang_velocity = motor_vel
# Keyframe motor on at frame 1
constraint.rigid_body_constraint.keyframe_insert(data_path="use_motor_ang", frame=1)
constraint.rigid_body_constraint.keyframe_insert(data_path="motor_ang_velocity", frame=1)
# Keyframe motor off at release_frame (free rotation)
constraint.rigid_body_constraint.use_motor_ang = False
constraint.rigid_body_constraint.keyframe_insert(data_path="use_motor_ang", frame=release_frame)

# 6. Create Projectile Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(proj_offset_x, 0.0, proj_loc_z))
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = (proj_size, proj_size, proj_size)
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = proj_mass
projectile.rigid_body.collision_shape = 'BOX'
# Slight friction to stick to arm initially
projectile.rigid_body.friction = 0.5

# 7. Set simulation length
bpy.context.scene.frame_end = sim_frames

# 8. Ensure proper collision margins (headless-safe)
for obj in [base, arm, projectile]:
    obj.rigid_body.use_margin = True
    obj.rigid_body.collision_margin = 0.04

# 9. Set gravity (default is -9.81 Z, which is fine)
print("Launcher constructed. Simulation ready.")