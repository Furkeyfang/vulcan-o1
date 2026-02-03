import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
base_rad = 1.5
base_h = 0.3
base_loc = (0.0, 0.0, 0.0)

tower_rad = 0.2
tower_h = 4.0
tower_loc = (0.0, 0.0, 2.3)  # base_h + tower_h/2

boom_len = 3.0
boom_w = 0.3
boom_d = 0.3
boom_loc = (0.0, 1.5, 4.3)  # tower top at 4.3, offset Y by half length

eff_sz = 0.2
eff_loc = (0.0, 3.0, 4.3)  # end of boom

hinge_piv = (0.0, 0.0, 4.3)
hinge_ax = (0.0, 0.0, 1.0)
motor_vel = 1.0

# 1. Create Base (Passive)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=base_rad,
    depth=base_h,
    location=base_loc
)
base = bpy.context.active_object
base.name = "Base"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# 2. Create Tower (Passive)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=tower_rad,
    depth=tower_h,
    location=tower_loc
)
tower = bpy.context.active_object
tower.name = "Tower"
bpy.ops.rigidbody.object_add()
tower.rigid_body.type = 'PASSIVE'

# 3. Create Boom (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=boom_loc)
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = (boom_d, boom_len, boom_w)  # X: depth, Y: length, Z: width
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'

# 4. Create End Effector (Active)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=eff_loc)
effector = bpy.context.active_object
effector.name = "EndEffector"
effector.scale = (eff_sz, eff_sz, eff_sz)
bpy.ops.rigidbody.object_add()
effector.rigid_body.type = 'ACTIVE'

# 5. Create Constraints
# Base-Tower: Fixed
bpy.ops.rigidbody.constraint_add()
const_fixed1 = bpy.context.active_object
const_fixed1.name = "Fixed_BaseTower"
const_fixed1.rigid_body_constraint.type = 'FIXED'
const_fixed1.rigid_body_constraint.object1 = base
const_fixed1.rigid_body_constraint.object2 = tower

# Tower-Boom: Hinge with Motor
bpy.ops.rigidbody.constraint_add()
const_hinge = bpy.context.active_object
const_hinge.name = "Hinge_TowerBoom"
const_hinge.rigid_body_constraint.type = 'HINGE'
const_hinge.rigid_body_constraint.object1 = tower
const_hinge.rigid_body_constraint.object2 = boom
const_hinge.rigid_body_constraint.pivot_type = 'CUSTOM'
const_hinge.location = hinge_piv
const_hinge.rigid_body_constraint.use_limit_ang_z = False
const_hinge.rigid_body_constraint.use_motor_ang = True
const_hinge.rigid_body_constraint.motor_ang_target_velocity = motor_vel

# Boom-EndEffector: Fixed
bpy.ops.rigidbody.constraint_add()
const_fixed2 = bpy.context.active_object
const_fixed2.name = "Fixed_BoomEffector"
const_fixed2.rigid_body_constraint.type = 'FIXED'
const_fixed2.rigid_body_constraint.object1 = boom
const_fixed2.rigid_body_constraint.object2 = effector

# 6. Set collision shapes (optimized)
for obj in [base, tower, boom, effector]:
    obj.rigid_body.collision_shape = 'MESH'

# 7. Verification Target (Visual only, non-physical)
bpy.ops.mesh.primitive_circle_add(
    vertices=32,
    radius=0.5,
    location=(2.5, 2.5, 4.3)
)
target = bpy.context.active_object
target.name = "TargetZone"
target.hide_render = True  # Keep in viewport but not render