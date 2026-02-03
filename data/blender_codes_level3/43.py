import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
beam_dim = (0.5, 0.5, 4.0)
beam_loc = (0.0, -1.5, 2.5)
arm_dim = (0.3, 3.0, 0.3)
arm_loc = (0.0, 0.0, 4.5)
holder_dim = (0.5, 0.5, 0.5)
holder_loc = (0.0, 1.5, 4.5)
hinge_loc = (0.0, -1.5, 4.5)
motor_velocity = 4.0
motor_torque = 100.0
holder_mass = 0.5
breaking_threshold = 50.0

# 1. Base (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. Support Beam (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "SupportBeam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'

# 3. Throwing Arm (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "ThrowingArm"
arm.scale = arm_dim
# Adjust arm origin to hinge end: move mesh 1.5m in -Y direction
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.translate(value=(0, -1.5, 0))
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
# Set initial rotation -90° (pointing down)
arm.rotation_euler = (math.radians(-90), 0, 0)

# 4. Projectile Holder (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=holder_loc)
holder = bpy.context.active_object
holder.name = "ProjectileHolder"
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.mass = holder_mass

# 5. Constraints
# 5a. Base-to-World (Fixed)
bpy.ops.rigidbody.constraint_add()
fix_base = bpy.context.active_object
fix_base.name = "BaseFix"
fix_base.rigid_body_constraint.type = 'FIXED'
fix_base.rigid_body_constraint.object1 = base

# 5b. Beam-to-Base (Fixed)
bpy.ops.rigidbody.constraint_add()
fix_beam = bpy.context.active_object
fix_beam.name = "BeamFix"
fix_beam.location = beam_loc
fix_beam.rigid_body_constraint.type = 'FIXED'
fix_beam.rigid_body_constraint.object1 = beam
fix_beam.rigid_body_constraint.object2 = base

# 5c. Arm-to-Beam Hinge (Motorized)
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.name = "Hinge"
hinge.location = hinge_loc
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = arm
hinge.rigid_body_constraint.object2 = beam
hinge.rigid_body_constraint.use_limit = False
hinge.rigid_body_constraint.use_motor = True
hinge.rigid_body_constraint.motor_type = 'VELOCITY'
hinge.rigid_body_constraint.motor_velocity = motor_velocity
hinge.rigid_body_constraint.motor_max_impulse = motor_torque

# 5d. Holder-to-Arm Fixed (Breakable)
bpy.ops.rigidbody.constraint_add()
holder_fix = bpy.context.active_object
holder_fix.name = "HolderFix"
holder_fix.location = holder_loc
holder_fix.rigid_body_constraint.type = 'FIXED'
holder_fix.rigid_body_constraint.object1 = holder
holder_fix.rigid_body_constraint.object2 = arm
holder_fix.rigid_body_constraint.use_breaking = True
holder_fix.rigid_body_constraint.breaking_threshold = breaking_threshold

# Set simulation environment
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10