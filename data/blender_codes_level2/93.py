import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define parameters from summary
platform_dim = (3.5, 1.0, 0.1)
platform_loc = (0.0, 0.0, 0.05)
beam_dim = (0.2, 0.2, 2.0)
beam_left_loc = (-1.65, 0.0, 1.0)
beam_right_loc = (1.65, 0.0, 1.0)
load_mass = 90.0
load_dim = (0.3, 0.3, 0.3)
load_loc = (0.0, 0.0, 0.1)
ground_dim = (10.0, 10.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)
simulation_frames = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create ground (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_dim
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'

# Create left vertical beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_left_loc)
beam_left = bpy.context.active_object
beam_left.name = "Beam_Left"
beam_left.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam_left.rigid_body.type = 'ACTIVE'
beam_left.rigid_body.mass = 50.0  # Estimated beam mass
beam_left.rigid_body.collision_shape = 'BOX'

# Create right vertical beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_right_loc)
beam_right = bpy.context.active_object
beam_right.name = "Beam_Right"
beam_right.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam_right.rigid_body.type = 'ACTIVE'
beam_right.rigid_body.mass = 50.0
beam_right.rigid_body.collision_shape = 'BOX'

# Create platform
bpy.ops.mesh.primitive_cube_add(size=1, location=platform_loc)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = platform_dim
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = 30.0  # Estimated platform mass
platform.rigid_body.collision_shape = 'BOX'

# Create load mass
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create fixed constraints (Generic with all axes locked)
def create_fixed_constraint(obj_a, obj_b, name):
    """Create a 6-DOF fixed constraint between two objects"""
    constraint = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(constraint)
    constraint.empty_display_type = 'ARROWS'
    
    constraint.rigid_body_constraint = constraint.rigid_body_constraint or 
        constraint.rigid_body_constraint_add()
    constraint.rigid_body_constraint.type = 'GENERIC'
    
    # Lock all linear and angular degrees
    constraint.rigid_body_constraint.use_limit_lin_x = True
    constraint.rigid_body_constraint.use_limit_lin_y = True
    constraint.rigid_body_constraint.use_limit_lin_z = True
    constraint.rigid_body_constraint.use_limit_ang_x = True
    constraint.rigid_body_constraint.use_limit_ang_y = True
    constraint.rigid_body_constraint.use_limit_ang_z = True
    
    # Set limits to zero (fully locked)
    for axis in ['lin_x', 'lin_y', 'lin_z', 'ang_x', 'ang_y', 'ang_z']:
        setattr(constraint.rigid_body_constraint, f'limit_{axis}_lower', 0.0)
        setattr(constraint.rigid_body_constraint, f'limit_{axis}_upper', 0.0)
    
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    
    return constraint

# Connect beams to ground
create_fixed_constraint(ground, beam_left, "Constraint_Ground_LeftBeam")
create_fixed_constraint(ground, beam_right, "Constraint_Ground_RightBeam")

# Connect platform to beams
create_fixed_constraint(beam_left, platform, "Constraint_LeftBeam_Platform")
create_fixed_constraint(beam_right, platform, "Constraint_RightBeam_Platform")

# Configure simulation
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.collection = bpy.context.scene.collection
bpy.context.scene.frame_end = simulation_frames

# Set gravity to Earth standard (-9.81 m/s²)
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Ensure proper collision margins
for obj in [ground, beam_left, beam_right, platform, load]:
    if hasattr(obj.rigid_body, 'collision_margin'):
        obj.rigid_body.collision_margin = 0.01

print("Diving platform structure created with fixed constraints.")
print(f"Simulation will run for {simulation_frames} frames.")