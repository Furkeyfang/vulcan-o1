import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
base_dim = (4.0, 2.0, 0.5)
base_loc = (0.0, 0.0, 0.0)

arm1_dim = (0.2, 2.0, 0.2)
arm1_loc = (0.0, 0.0, 0.25)
arm1_pivot = (0.0, -1.0, 0.25)

arm2_dim = (0.2, 1.5, 0.2)
arm2_loc = (0.0, 1.0, 0.25)
arm2_pivot = (0.0, 0.75, 0.25)

projectile_dim = (0.3, 0.3, 0.3)
projectile_loc = (0.0, 1.75, 0.4)

hinge1_velocity = 6.0
hinge2_velocity = 8.0
hinge2_activation_frame = 10
simulation_frames = 100

# Set end frame for animation
bpy.context.scene.frame_end = simulation_frames

# 1. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Create First-stage Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm1_loc)
arm1 = bpy.context.active_object
arm1.name = "Arm1"
arm1.scale = arm1_dim
bpy.ops.rigidbody.object_add()
arm1.rigid_body.type = 'ACTIVE'
arm1.rigid_body.collision_shape = 'BOX'
arm1.rigid_body.use_margin = True
arm1.rigid_body.collision_margin = 0.0

# 3. Create Second-stage Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm2_loc)
arm2 = bpy.context.active_object
arm2.name = "Arm2"
arm2.scale = arm2_dim
bpy.ops.rigidbody.object_add()
arm2.rigid_body.type = 'ACTIVE'
arm2.rigid_body.collision_shape = 'BOX'
arm2.rigid_body.use_margin = True
arm2.rigid_body.collision_margin = 0.0

# 4. Create Projectile
bpy.ops.mesh.primitive_cube_add(size=1.0, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = projectile_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = 0.5  # Lower mass for better launch

# 5. Create Hinge Constraints (using generic constraints, not rigid body joints)
# Hinge1: Base to Arm1
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm1_pivot)
hinge1_empty = bpy.context.active_object
hinge1_empty.name = "Hinge1_Empty"
hinge1_empty.empty_display_size = 0.2

constraint1 = arm1.constraints.new('RIGID_BODY_JOINT')
constraint1.object1 = base
constraint1.object2 = arm1
constraint1.pivot_type = 'CUSTOM'
constraint1.pivot_x = arm1_pivot[0]
constraint1.pivot_y = arm1_pivot[1]
constraint1.pivot_z = arm1_pivot[2]
constraint1.use_angular_x = False
constraint1.use_angular_y = True  # Allow rotation around Y
constraint1.use_angular_z = False
constraint1.use_limit_ang_y = False
constraint1.use_motor_ang_y = True
constraint1.motor_ang_velocity = hinge1_velocity
constraint1.motor_ang_max_torque = 100.0  # High torque to achieve velocity quickly

# Hinge2: Arm1 to Arm2
bpy.ops.object.empty_add(type='PLAIN_AXES', location=arm2_pivot)
hinge2_empty = bpy.context.active_object
hinge2_empty.name = "Hinge2_Empty"
hinge2_empty.empty_display_size = 0.2

constraint2 = arm2.constraints.new('RIGID_BODY_JOINT')
constraint2.object1 = arm1
constraint2.object2 = arm2
constraint2.pivot_type = 'CUSTOM'
constraint2.pivot_x = arm2_pivot[0]
constraint2.pivot_y = arm2_pivot[1]
constraint2.pivot_z = arm2_pivot[2]
constraint2.use_angular_x = False
constraint2.use_angular_y = True
constraint2.use_angular_z = False
constraint2.use_limit_ang_y = False
constraint2.use_motor_ang_y = True
constraint2.motor_ang_velocity = 0.0  # Start disabled
constraint2.motor_ang_max_torque = 100.0

# 6. Animate hinge motor activation
# Hinge1: active from frame 0
constraint1.keyframe_insert(data_path="motor_ang_velocity", frame=0)
constraint1.keyframe_insert(data_path="use_motor_ang_y", frame=0)

# Hinge2: disabled until activation frame
constraint2.keyframe_insert(data_path="motor_ang_velocity", frame=0)
constraint2.keyframe_insert(data_path="use_motor_ang_y", frame=0)

# Enable at activation frame
constraint2.motor_ang_velocity = hinge2_velocity
constraint2.keyframe_insert(data_path="motor_ang_velocity", frame=hinge2_activation_frame)
constraint2.use_motor_ang_y = True
constraint2.keyframe_insert(data_path="use_motor_ang_y", frame=hinge2_activation_frame)

# 7. Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Ensure all objects are properly linked
for obj in [base, arm1, arm2, projectile, hinge1_empty, hinge2_empty]:
    bpy.context.collection.objects.link(obj)