import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ====== PARAMETERS ======
platform_dim = (3.0, 3.0, 0.5)
platform_loc = (0.0, 0.0, 0.0)

crane_dim = (2.0, 2.0, 1.0)
crane_loc = (0.0, 0.0, 0.75)

hinge_pivot = (0.0, 0.0, 0.75)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 0.785  # rad/s (π/4)

# ====== STATIONARY PLATFORM ======
bpy.ops.mesh.primitive_cube_add(size=1.0, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Stationary_Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'PASSIVE'
platform.rigid_body.collision_shape = 'BOX'

# ====== ROTATING CRANE BASE ======
bpy.ops.mesh.primitive_cube_add(size=1.0, location=crane_loc)
crane_base = bpy.context.active_object
crane_base.name = "Rotating_Crane_Base"
crane_base.scale = crane_dim
bpy.ops.rigidbody.object_add()
crane_base.rigid_body.type = 'ACTIVE'
crane_base.rigid_body.collision_shape = 'BOX'

# ====== HINGE CONSTRAINT ======
# Create empty object as constraint anchor
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Hinge_Constraint"

# Add rigid body constraint to the empty
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.object1 = platform
constraint.object2 = crane_base
constraint.use_limit_ang_z = False  # Allow continuous rotation
constraint.use_motor_ang_z = True
constraint.motor_ang_target_velocity = motor_velocity
constraint.motor_ang_max_impulse = 5.0  # Reasonable torque limit

# Set hinge axis in world space (empty's local Z)
constraint_empty.rotation_euler = (0.0, 0.0, 0.0)  # Ensure alignment
constraint.axis = hinge_axis

# ====== SCENE SETUP ======
# Ensure rigid body world exists and gravity is on
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

print("Motorized crane base constructed. Hinge motor enabled.")