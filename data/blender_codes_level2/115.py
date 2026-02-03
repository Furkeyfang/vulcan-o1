import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
pier_base_x = 1.0
pier_base_y = 1.0
pier_height = 3.0
pier_center = mathutils.Vector((0.0, 0.0, 1.5))

arm_length = 5.5
arm_width = 0.5
arm_height = 0.5
arm_center = mathutils.Vector((2.75, 0.0, 3.25))

load_size = 0.5
load_mass = 900.0
load_center = mathutils.Vector((5.75, 0.0, 3.75))

concrete_density = 2400.0
simulation_frames = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# 1. Create Pier (Passive Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pier_center)
pier = bpy.context.active_object
pier.name = "Pier"
pier.scale = (pier_base_x, pier_base_y, pier_height)

# Calculate pier volume for mass
pier_volume = pier_base_x * pier_base_y * pier_height
pier_mass = pier_volume * concrete_density

bpy.ops.rigidbody.object_add()
pier.rigid_body.type = 'PASSIVE'
pier.rigid_body.mass = pier_mass
pier.rigid_body.collision_shape = 'BOX'
pier.rigid_body.friction = 0.5
pier.rigid_body.restitution = 0.1

# 2. Create Arm (Active Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_center)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_length, arm_width, arm_height)

arm_volume = arm_length * arm_width * arm_height
arm_mass = arm_volume * concrete_density

bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.mass = arm_mass
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.friction = 0.5
arm.rigid_body.restitution = 0.1

# 3. Create Load (Active Rigid Body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_center)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)

bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.friction = 0.5
load.rigid_body.restitution = 0.1

# 4. Create Fixed Constraints
def create_fixed_constraint(obj1, obj2, name):
    """Create a FIXED rigid body constraint between two objects"""
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = name
    
    # Add constraint to empty
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    # Baumgarte stabilization for rigidity
    constraint.use_breaking = False
    constraint.breaking_threshold = 10000.0
    constraint.use_override_solver_iterations = True
    constraint.solver_iterations = 50
    
    return constraint_empty

# Pier to Arm constraint
create_fixed_constraint(pier, arm, "Pier_Arm_Constraint")

# Arm to Load constraint
create_fixed_constraint(arm, load, "Arm_Load_Constraint")

# 5. Configure Simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10

# 6. Bake simulation (headless)
print("Simulating cantilever bridge pier...")
for frame in range(simulation_frames + 1):
    bpy.context.scene.frame_set(frame)
    bpy.ops.rigidbody.world_simulate()

# Verification check
final_load_pos = load.matrix_world.translation
initial_load_pos = load_center
displacement = (final_load_pos - initial_load_pos).length
print(f"Load displacement after {simulation_frames} frames: {displacement:.6f} m")
if displacement < 0.01:
    print("VERIFIED: Structure stable (displacement < 1 cm)")
else:
    print("WARNING: Excessive displacement detected")