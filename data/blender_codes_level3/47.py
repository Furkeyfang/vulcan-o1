import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
base_dim = (5.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
hinge_loc = (0.0, 0.0, 0.75)
arm_dim = (0.3, 4.0, 0.3)
arm_length = 4.0
arm_angle_deg = -5.0
arm_angle_rad = math.radians(arm_angle_deg)
counter_dim = (1.0, 1.0, 1.0)
counter_loc = (-2.0, 0.0, 1.0)
proj_dim = (0.8, 0.8, 0.8)
proj_loc = (3.985, 0.0, 0.4)
motor_velocity = 3.0
arm_mass = 50.0
counter_mass = 100.0
proj_mass = 20.0

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.mass = 1000.0  # Very heavy static base

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
arm = bpy.context.active_object
arm.scale = arm_dim
# Position arm: pivot at hinge, rotated
arm.location = hinge_loc
arm.rotation_euler = (0, arm_angle_rad, 0)
# Move arm so hinge is at one end: arm length extends along local +X
# Cube center is at hinge, but we want hinge at one end. Shift by -arm_length/2 in local X
arm.location.x += (arm_length/2) * math.cos(arm_angle_rad)
arm.location.z += (arm_length/2) * math.sin(arm_angle_rad)
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass
arm.rigid_body.collision_shape = 'BOX'

# Create Counterweight
bpy.ops.mesh.primitive_cube_add(size=1, location=counter_loc)
counter = bpy.context.active_object
counter.scale = counter_dim
bpy.ops.rigidbody.object_add()
counter.rigid_body.type = 'PASSIVE'
counter.rigid_body.mass = counter_mass

# Create Projectile
bpy.ops.mesh.primitive_cube_add(size=1, location=proj_loc)
proj = bpy.context.active_object
proj.scale = proj_dim
bpy.ops.rigidbody.object_add()
proj.rigid_body.type = 'ACTIVE'
proj.rigid_body.mass = proj_mass

# Create Hinge Constraint between Base and Arm
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = base
constraint.rigid_body_constraint.object2 = arm
constraint.location = hinge_loc
constraint.rigid_body_constraint.use_limit_ang_z = True
constraint.rigid_body_constraint.limit_ang_z_lower = math.radians(-90)
constraint.rigid_body_constraint.limit_ang_z_upper = math.radians(45)
# Set motor
constraint.rigid_body_constraint.use_motor_ang = True
constraint.rigid_body_constraint.motor_ang_velocity = motor_velocity
constraint.rigid_body_constraint.motor_ang_max_torque = 1000.0

# Create Fixed Constraint between Base and Counterweight
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
counter.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = base
constraint2.rigid_body_constraint.object2 = counter
constraint2.location = counter_loc

# Set up world physics
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.gravity = (0, 0, -9.81)

# Ensure all objects have collision
for obj in [base, arm, counter, proj]:
    if obj.rigid_body:
        obj.rigid_body.collision_shape = 'BOX'
        obj.rigid_body.collision_margin = 0.0

print("Catapult assembly complete. Motor hinge set to", motor_velocity, "rad/s.")