import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Define parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

arm_dim = (4.0, 0.2, 0.2)
arm_loc = (2.0, 0.0, 0.6)
arm_pivot = (0.0, 0.0, 0.25)

cw_dim = (1.0, 1.0, 1.0)
cw_loc = (-1.0, 0.0, 1.2)
cw_mass = 50.0

proj_dim = (0.3, 0.3, 0.3)
proj_loc = (4.0, 0.0, 0.85)
proj_mass = 0.5

hinge_axis = (0.0, 1.0, 0.0)
motor_velocity = 6.0

# 1. Create Base Platform (Passive)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Create Lever Arm (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "LeverArm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = 5.0  # Moderate mass for arm

# 3. Create Counterweight (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cw_loc)
cw = bpy.context.active_object
cw.name = "Counterweight"
cw.scale = cw_dim
bpy.ops.rigidbody.object_add()
cw.rigid_body.type = 'ACTIVE'
cw.rigid_body.collision_shape = 'BOX'
cw.rigid_body.mass = cw_mass

# 4. Create Projectile (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=proj_loc)
proj = bpy.context.active_object
proj.name = "Projectile"
proj.scale = proj_dim
bpy.ops.rigidbody.object_add()
proj.rigid_body.type = 'ACTIVE'
proj.rigid_body.collision_shape = 'BOX'
proj.rigid_body.mass = proj_mass

# 5. Parent Counterweight to Arm (for fixed attachment)
cw.parent = arm
cw.matrix_parent_inverse = arm.matrix_world.inverted()

# 6. Create Hinge Constraint between Base and Arm
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.rigidbody.connect()

# Configure hinge
constraint = arm.rigid_body_constraints[-1]
constraint.type = 'HINGE'
constraint.object1 = base
constraint.pivot_type = 'CUSTOM'
constraint.pivot_x = arm_pivot[0]
constraint.pivot_y = arm_pivot[1]
constraint.pivot_z = arm_pivot[2]
constraint.use_limit_z = False
constraint.use_motor_z = True
constraint.motor_lin_target_velocity = motor_velocity
constraint.motor_lin_velocity = motor_velocity

# 7. Set collision margins (prevent penetration)
for obj in [base, arm, cw, proj]:
    obj.rigid_body.collision_margin = 0.001

# 8. Set initial rotation for visual clarity (arm horizontal)
arm.rotation_euler = (0.0, 0.0, 0.0)

# 9. Configure world physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50