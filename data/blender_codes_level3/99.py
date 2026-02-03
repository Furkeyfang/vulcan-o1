import bpy
import math

# 1. Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define variables from parameter summary
base_dim = (2.0, 2.0, 0.2)
base_loc = (0.0, 0.0, 0.1)
arm_dim = (3.0, 0.5, 0.2)
arm_loc = (0.0, 0.0, 0.3)
hinge_pivot = (0.0, 0.0, 0.2)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 2.0

# 3. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "BasePlatform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 4. Create Rotating Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "RotatingArm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'

# 5. Add Hinge Constraint between Base and Arm
# We'll add constraint to arm and set base as target
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Hinge_Motor"
constraint.empty_display_type = 'ARROWS'

# Set constraint type and properties
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = arm
constraint.rigid_body_constraint.object2 = base

# Set pivot location (in world coordinates)
constraint.rigid_body_constraint.pivot_type = 'LOCATION'
constraint.rigid_body_constraint.use_override_solver_iterations = True
constraint.rigid_body_constraint.pivot_x = hinge_pivot[0]
constraint.rigid_body_constraint.pivot_y = hinge_pivot[1]
constraint.rigid_body_constraint.pivot_z = hinge_pivot[2]

# Set axis (world Z)
constraint.rigid_body_constraint.axis = hinge_axis

# Enable motor and set velocity
constraint.rigid_body_constraint.use_motor = True
constraint.rigid_body_constraint.motor_velocity = motor_velocity

# 6. Set initial arm alignment along X-axis (ensure no rotation)
arm.rotation_euler = (0.0, 0.0, 0.0)

# 7. Optional: Set simulation parameters for consistency
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 10

print("Hinge-turn robot constructed successfully.")
print(f"Motor velocity: {motor_velocity} rad/s")
print("Arm initial orientation: 0 degrees about Z-axis")