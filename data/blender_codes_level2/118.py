import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
tower_dim = (0.5, 0.5, 3.0)
tower_loc = (0.0, 0.0, 1.5)
arm_dim = (2.5, 0.3, 0.3)
arm_loc = (1.25, 0.0, 3.15)
load_dim = (0.4, 0.4, 0.4)
load_loc = (2.5, 0.0, 3.5)
load_mass = 180.0
constraint_breaking_force = 10000.0
simulation_frames = 100

# Create vertical support tower
bpy.ops.mesh.primitive_cube_add(size=1.0, location=tower_loc)
tower = bpy.context.active_object
tower.name = "Tower"
tower.scale = tower_dim
bpy.ops.rigidbody.object_add()
tower.rigid_body.type = 'PASSIVE'
tower.rigid_body.collision_shape = 'BOX'

# Create horizontal arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.linear_damping = 0.1
arm.rigid_body.angular_damping = 0.1

# Create load block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'BOX'
load.rigid_body.mass = load_mass
load.rigid_body.linear_damping = 0.1
load.rigid_body.angular_damping = 0.1

# Create fixed constraint between tower and arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 3.0))
constraint1 = bpy.context.active_object
constraint1.name = "Tower_Arm_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = tower
constraint1.rigid_body_constraint.object2 = arm
constraint1.rigid_body_constraint.breaking_threshold = constraint_breaking_force

# Create fixed constraint between arm and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=load_loc)
constraint2 = bpy.context.active_object
constraint2.name = "Arm_Load_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint2.rigid_body_constraint.type = 'FIXED'
constraint2.rigid_body_constraint.object1 = arm
constraint2.rigid_body_constraint.object2 = load
constraint2.rigid_body_constraint.breaking_threshold = constraint_breaking_force

# Configure physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Set simulation length
bpy.context.scene.frame_end = simulation_frames

# Run simulation (headless compatible)
for frame in range(simulation_frames + 1):
    bpy.context.scene.frame_set(frame)
    # Optional: Log positions for verification
    if frame % 20 == 0:
        print(f"Frame {frame}: Load at {load.location}, Arm at {arm.location}")

# Final stability check
initial_load_z = load_loc[2]
final_load_z = load.location.z
displacement = abs(final_load_z - initial_load_z)
print(f"
Simulation Complete:")
print(f"Initial load Z: {initial_load_z:.3f}m")
print(f"Final load Z: {final_load_z:.3f}m")
print(f"Vertical displacement: {displacement:.3f}m")
print(f"Structure {'STABLE' if displacement < 0.1 else 'FAILED'}")