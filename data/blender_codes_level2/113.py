import bpy
import math

# ========== 1. CLEAR SCENE ==========
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# ========== 2. PARAMETERS FROM SUMMARY ==========
# Column
col_size = (1.0, 1.0, 3.0)
col_loc = (0.0, 0.0, 1.5)

# Arm
arm_size = (6.0, 0.5, 0.5)
arm_loc = (3.0, 0.0, 3.0)

# Counterweight
cw_radius = 0.75
cw_depth = 0.5
cw_loc = (0.75, 0.0, 3.0)

# Hook
hook_radius = 0.2
hook_depth = 0.3
hook_loc = (6.0, 0.0, 3.0)

# Load
load_size = 0.8
load_mass = 800.0
load_init_loc = (6.0, 0.0, 0.4)

# Physics
motor_velocity = 0.5
motor_max_torque = 5000.0
constraint_stiffness = 1000.0
constraint_damping = 10.0
density_steel = 7850.0

# ========== 3. CREATE COLUMN ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_size[0], col_size[1], col_size[2])
# Rigid body (passive, fixed to ground)
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# ========== 4. CREATE ARM ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_size[0], arm_size[1], arm_size[2])
# Calculate volume and set mass from steel density
arm_vol = arm_size[0] * arm_size[1] * arm_size[2]
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_vol * density_steel
arm.rigid_body.collision_shape = 'BOX'

# ========== 5. CREATE COUNTERWEIGHT ==========
bpy.ops.mesh.primitive_cylinder_add(
    radius=cw_radius,
    depth=cw_depth,
    location=cw_loc
)
counterweight = bpy.context.active_object
counterweight.name = "Counterweight"
counterweight.rotation_euler = (math.pi/2, 0, 0)  # Orient along X
# Mass from steel density
cw_vol = math.pi * cw_radius**2 * cw_depth
bpy.ops.rigidbody.object_add()
counterweight.rigid_body.type = 'ACTIVE'
counterweight.rigid_body.mass = cw_vol * density_steel
counterweight.rigid_body.collision_shape = 'CONVEX_HULL'

# ========== 6. CREATE HOOK ==========
bpy.ops.mesh.primitive_cylinder_add(
    radius=hook_radius,
    depth=hook_depth,
    location=hook_loc
)
hook = bpy.context.active_object
hook.name = "Hook"
hook.rotation_euler = (math.pi/2, 0, 0)  # Orient along X
# Steel mass
hook_vol = math.pi * hook_radius**2 * hook_depth
bpy.ops.rigidbody.object_add()
hook.rigid_body.type = 'ACTIVE'
hook.rigid_body.mass = hook_vol * density_steel
hook.rigid_body.collision_shape = 'CONVEX_HULL'

# ========== 7. CREATE LOAD ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_init_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# ========== 8. CREATE CONSTRAINTS ==========
# Column-Arm HINGE (motorized)
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.name = "Hinge_Column_Arm"
hinge.rigid_body_constraint.type = 'HINGE'
# Set pivot at column top (0,0,3)
hinge.location = (0, 0, 3)
# Link objects
hinge.rigid_body_constraint.object1 = column
hinge.rigid_body_constraint.object2 = arm
# Motor settings
hinge.rigid_body_constraint.use_motor = True
hinge.rigid_body_constraint.motor_velocity = motor_velocity
hinge.rigid_body_constraint.motor_max_torque = motor_max_torque
# Constraint stiffness
hinge.rigid_body_constraint.stiffness = constraint_stiffness
hinge.rigid_body_constraint.damping = constraint_damping

# Arm-Counterweight FIXED
bpy.ops.rigidbody.constraint_add()
fixed1 = bpy.context.active_object
fixed1.name = "Fixed_Arm_Counterweight"
fixed1.rigid_body_constraint.type = 'FIXED'
fixed1.location = cw_loc
fixed1.rigid_body_constraint.object1 = arm
fixed1.rigid_body_constraint.object2 = counterweight
fixed1.rigid_body_constraint.stiffness = constraint_stiffness
fixed1.rigid_body_constraint.damping = constraint_damping

# Arm-Hook FIXED
bpy.ops.rigidbody.constraint_add()
fixed2 = bpy.context.active_object
fixed2.name = "Fixed_Arm_Hook"
fixed2.rigid_body_constraint.type = 'FIXED'
fixed2.location = hook_loc
fixed2.rigid_body_constraint.object1 = arm
fixed2.rigid_body_constraint.object2 = hook
fixed2.rigid_body_constraint.stiffness = constraint_stiffness
fixed2.rigid_body_constraint.damping = constraint_damping

# Hook-Load FIXED
bpy.ops.rigidbody.constraint_add()
fixed3 = bpy.context.active_object
fixed3.name = "Fixed_Hook_Load"
fixed3.rigid_body_constraint.type = 'FIXED'
fixed3.location = hook_loc
fixed3.rigid_body_constraint.object1 = hook
fixed3.rigid_body_constraint.object2 = load
fixed3.rigid_body_constraint.stiffness = constraint_stiffness
fixed3.rigid_body_constraint.damping = constraint_damping

# ========== 9. SET SCENE PHYSICS ==========
bpy.context.scene.gravity = (0, 0, -9.81)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = 100

print("Cantilever crane assembly complete. Ready for simulation.")