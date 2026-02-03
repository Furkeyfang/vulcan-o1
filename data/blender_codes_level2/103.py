import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
tower_sz = (1.0, 1.0, 6.0)
tower_ctr = (0.5, 0.5, 3.0)
arm_sz = (5.0, 1.0, 1.0)
arm_ctr = (2.5, 0.5, 6.5)
counter_sz = (2.0, 2.0, 0.5)
counter_ctr = (-2.0, 0.0, 6.5)
hook_sz = (0.2, 0.2, 0.2)
hook_ctr = (5.0, 0.0, 6.5)
load_mass = 900.0
load_sz = (0.5, 0.5, 0.5)
load_ctr = (5.0, 0.0, 5.0)
constr_tower_arm = (0.0, 0.0, 6.0)
constr_arm_counter = (-2.0, 0.0, 6.5)
constr_arm_hook = (5.0, 0.0, 6.5)
frames = 100

# Create ground plane (passive)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0,0,-0.25))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create vertical tower
bpy.ops.mesh.primitive_cube_add(size=1, location=tower_ctr)
tower = bpy.context.active_object
tower.name = "Tower"
tower.scale = tower_sz
bpy.ops.rigidbody.object_add()
tower.rigid_body.type = 'PASSIVE'

# Create horizontal arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_ctr)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_sz
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'

# Create counterweight platform
bpy.ops.mesh.primitive_cube_add(size=1, location=counter_ctr)
counter = bpy.context.active_object
counter.name = "Counterweight"
counter.scale = counter_sz
bpy.ops.rigidbody.object_add()
counter.rigid_body.type = 'PASSIVE'

# Create hook point
bpy.ops.mesh.primitive_cube_add(size=1, location=hook_ctr)
hook = bpy.context.active_object
hook.name = "Hook"
hook.scale = hook_sz
bpy.ops.rigidbody.object_add()
hook.rigid_body.type = 'PASSIVE'

# Create load mass (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1, location=load_ctr)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_sz
bpy.ops.rigidbody.object_add()
load.rigid_body.mass = load_mass
load.rigid_body.type = 'ACTIVE'

# Add fixed constraints
def add_fixed_constraint(name, location, obj1, obj2):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = f"Constraint_{name}"
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2

# Tower-Arm constraint
add_fixed_constraint("TowerArm", constr_tower_arm, tower, arm)

# Arm-Counterweight constraint
add_fixed_constraint("ArmCounter", constr_arm_counter, arm, counter)

# Arm-Hook constraint
add_fixed_constraint("ArmHook", constr_arm_hook, arm, hook)

# Hook-Load constraint (to apply force)
add_fixed_constraint("HookLoad", hook_ctr, hook, load)

# Set up simulation
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = frames

# Run simulation in background
bpy.ops.ptcache.bake_all(bake=True)