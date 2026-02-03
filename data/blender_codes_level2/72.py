import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
pole_radius = 0.2
pole_height = 6.0
pole_loc = (0.0, 0.0, 3.0)

arm_radius = 0.1
arm_length = 1.5
arm_loc = (0.0, 0.0, 6.0)

load_size = 0.3
load_mass = 50.0
load_loc = (0.75, 0.0, 6.0)

ground_size = (10.0, 10.0, 1.0)
ground_loc = (0.0, 0.0, -0.5)

constraint_base = (0.0, 0.0, 0.0)
constraint_joint = (0.0, 0.0, 6.0)
constraint_load = (0.75, 0.0, 6.0)

sim_frames = 100

# Create ground (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create pole cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=pole_radius,
    depth=pole_height,
    location=pole_loc
)
pole = bpy.context.active_object
pole.name = "Pole"
bpy.ops.rigidbody.object_add()
pole.rigid_body.type = 'ACTIVE'
pole.rigid_body.kinematic = True  # Start kinematic

# Create arm cylinder (horizontal)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=24,
    radius=arm_radius,
    depth=arm_length,
    location=arm_loc
)
arm = bpy.context.active_object
arm.name = "Arm"
arm.rotation_euler = (0.0, math.radians(90.0), 0.0)  # Rotate to horizontal
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.kinematic = True  # Start kinematic

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.kinematic = True  # Start kinematic

# Create FIXED constraints using empty objects
def create_fixed_constraint(obj1, obj2, pivot, name):
    # Create empty at pivot point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj1
    constraint.object2 = obj2
    
    return empty

# Constraint: Ground to Pole base
create_fixed_constraint(ground, pole, constraint_base, "Constraint_Base")

# Constraint: Pole to Arm joint
create_fixed_constraint(pole, arm, constraint_joint, "Constraint_Joint")

# Constraint: Arm to Load
create_fixed_constraint(arm, load, constraint_load, "Constraint_Load")

# Set up simulation parameters
scene = bpy.context.scene
scene.frame_end = sim_frames
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

# Keyframe transition from kinematic to dynamic
# Frame 1: All parts kinematic (frozen)
pole.rigid_body.kinematic = True
arm.rigid_body.kinematic = True
load.rigid_body.kinematic = True

pole.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
arm.keyframe_insert(data_path='rigid_body.kinematic', frame=1)
load.keyframe_insert(data_path='rigid_body.kinematic', frame=1)

# Frame 2: Load becomes dynamic (subject to gravity)
load.rigid_body.kinematic = False
load.keyframe_insert(data_path='rigid_body.kinematic', frame=2)

# Frame 3: Arm becomes dynamic (connected via constraints)
arm.rigid_body.kinematic = False
arm.keyframe_insert(data_path='rigid_body.kinematic', frame=3)

# Frame 4: Pole becomes dynamic (final release)
pole.rigid_body.kinematic = False
pole.keyframe_insert(data_path='rigid_body.kinematic', frame=4)

# Bake physics simulation
bpy.ops.ptcache.bake(bake=True)

print("Streetlight structure created and simulated for", sim_frames, "frames.")
print("Check for stability and constraint integrity.")