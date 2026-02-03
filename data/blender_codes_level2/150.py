import bpy
import mathutils
from mathutils import Vector, Matrix
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define parameters from summary
beam_len_base = 10.0
beam_len_vert = 10.0
beam_cross = 0.3
vA = Vector((5.0, 0.0, 0.0))
vB = Vector((-2.5, 4.33, 0.0))
vC = Vector((-2.5, -4.33, 0.0))
base_center = Vector((0.0, 0.0, 0.0))
apex = Vector((0.0, 0.0, 10.0))
platform_dim = (1.0, 1.0, 0.2)
platform_loc = (0.0, 0.0, 10.0)
load_mass = 250.0
sim_frames = 100
pos_tol = 0.1
gravity_val = -9.81

# Set up physics world
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0, 0, gravity_val)
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Function to create a beam between two points
def create_beam(start, end, name, passive=True):
    """Create a beam with given start and end points"""
    # Calculate midpoint and direction
    mid = (start + end) / 2
    direction = end - start
    length = direction.length
    
    # Create cube and scale to beam dimensions
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    beam = bpy.context.active_object
    beam.name = name
    
    # Scale: default cube is 2x2x2, so divide by 2
    beam.scale = (length/2, beam_cross/2, beam_cross/2)
    
    # Rotate to align with direction vector
    # Default cube's local X-axis will align with beam direction
    rot_quat = Vector((1, 0, 0)).rotation_difference(direction)
    beam.rotation_mode = 'QUATERNION'
    beam.rotation_quaternion = rot_quat
    
    # Apply scale and rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if passive:
        beam.rigid_body.type = 'PASSIVE'
        beam.rigid_body.collision_shape = 'BOX'
    else:
        beam.rigid_body.type = 'ACTIVE'
        beam.rigid_body.collision_shape = 'BOX'
        beam.rigid_body.mass = 50.0  # Estimated beam mass
    
    return beam

# Function to create fixed constraint between two objects at a point
def create_fixed_constraint(obj1, obj2, location, name):
    """Create fixed constraint at specified location"""
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"constraint_{name}"
    constraint.location = location
    
    # Configure fixed constraint
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    constraint.rigid_body_constraint.use_override_solver_iterations = True
    constraint.rigid_body_constraint.solver_iterations = 20
    
    # Parent constraint to empty for organization
    constraint.parent = empty
    
    return constraint

# Create base beams (passive)
beam_AB = create_beam(vA, vB, "beam_AB", passive=True)
beam_BC = create_beam(vB, vC, "beam_BC", passive=True)
beam_CA = create_beam(vC, vA, "beam_CA", passive=True)

# Create vertical beam (active)
beam_vert = create_beam(base_center, apex, "beam_vertical", passive=False)

# Create platform cube at apex
bpy.ops.mesh.primitive_cube_add(size=1, location=platform_loc)
platform = bpy.context.active_object
platform.name = "observation_platform"
platform.scale = (platform_dim[0]/2, platform_dim[1]/2, platform_dim[2]/2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add rigid body to platform
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.mass = load_mass  # 250kg load

# Create fixed constraints at base triangle vertices
constraint_A = create_fixed_constraint(beam_AB, beam_CA, vA, "joint_A")
constraint_B = create_fixed_constraint(beam_AB, beam_BC, vB, "joint_B")
constraint_C = create_fixed_constraint(beam_BC, beam_CA, vC, "joint_C")

# Create fixed constraint at base center (connecting all base beams to vertical beam)
# Need multiple constraints for multiple connections
constraint_center_AB = create_fixed_constraint(beam_AB, beam_vert, base_center, "joint_center_AB")
constraint_center_BC = create_fixed_constraint(beam_BC, beam_vert, base_center, "joint_center_BC")
constraint_center_CA = create_fixed_constraint(beam_CA, beam_vert, base_center, "joint_center_CA")

# Create fixed constraint at apex (connecting vertical beam to platform)
constraint_apex = create_fixed_constraint(beam_vert, platform, apex, "joint_apex")

# Set up simulation
bpy.context.scene.frame_end = sim_frames

# Bake physics simulation
print("Baking physics simulation...")
bpy.ops.ptcache.bake_all(bake=True)

# Verify stability by checking platform position at last frame
bpy.context.scene.frame_set(sim_frames)
final_pos = platform.location
initial_pos = Vector(platform_loc)
displacement = (final_pos - initial_pos).length

print(f"Platform initial position: {initial_pos}")
print(f"Platform final position: {final_pos}")
print(f"Displacement magnitude: {displacement:.4f} m")
print(f"Tolerance: {pos_tol} m")

if displacement <= pos_tol:
    print("✓ Structure stable: displacement within tolerance")
else:
    print("✗ Structure unstable: displacement exceeds tolerance")

# Optional: Save blend file for inspection
# bpy.ops.wm.save_as_mainfile(filepath="/tmp/tetrahedral_tower.blend")