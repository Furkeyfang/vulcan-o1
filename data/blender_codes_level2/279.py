import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
beam_dim = (4.0, 0.3, 0.3)
beam_loc = (0.0, 0.0, 2.0)
left_leg_dim = (0.3, 0.3, 3.464)
left_leg_top = (-2.0, 0.0, 2.0)
left_leg_bottom = (-5.0, 0.0, 0.268)
left_leg_rot = 1.0472  # 60° in radians
right_leg_dim = (0.3, 0.3, 3.864)
right_leg_top = (2.0, 0.0, 2.0)
right_leg_bottom = (5.732, 0.0, 1.0)
right_leg_rot = -1.3090  # -75° in radians
load_dim = (1.0, 1.0, 0.5)
load_mass = 2500.0
load_loc = (0.0, 0.0, 2.4)
ground_dim = (20.0, 20.0, 0.5)
ground_loc = (0.0, 0.0, -0.25)
simulation_frames = 100
solver_iterations = 50

# Configure physics world
bpy.context.scene.rigidbody_world.points_cache.frame_start = 1
bpy.context.scene.rigidbody_world.points_cache.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.frame_end = simulation_frames

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1, location=ground_loc)
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = ground_dim
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create central beam
bpy.ops.mesh.primitive_cube_add(size=1, location=beam_loc)
beam = bpy.context.active_object
beam.name = "Beam"
beam.scale = beam_dim
bpy.ops.rigidbody.object_add()
beam.rigid_body.type = 'PASSIVE'

# Create left leg (60°)
left_leg_center = (
    (left_leg_top[0] + left_leg_bottom[0]) / 2,
    (left_leg_top[1] + left_leg_bottom[1]) / 2,
    (left_leg_top[2] + left_leg_bottom[2]) / 2
)
bpy.ops.mesh.primitive_cube_add(size=1, location=left_leg_center)
left_leg = bpy.context.active_object
left_leg.name = "LeftLeg"
left_leg.scale = left_leg_dim
left_leg.rotation_euler = (0, left_leg_rot, 0)
bpy.ops.rigidbody.object_add()
left_leg.rigid_body.type = 'PASSIVE'

# Create right leg (75°)
right_leg_center = (
    (right_leg_top[0] + right_leg_bottom[0]) / 2,
    (right_leg_top[1] + right_leg_bottom[1]) / 2,
    (right_leg_top[2] + right_leg_bottom[2]) / 2
)
bpy.ops.mesh.primitive_cube_add(size=1, location=right_leg_center)
right_leg = bpy.context.active_object
right_leg.name = "RightLeg"
right_leg.scale = right_leg_dim
right_leg.rotation_euler = (0, right_leg_rot, 0)
bpy.ops.rigidbody.object_add()
right_leg.rigid_body.type = 'PASSIVE'

# Create load cube
bpy.ops.mesh.primitive_cube_add(size=1, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Create fixed constraints
def create_fixed_constraint(obj1, obj2, pivot_world):
    bpy.ops.object.select_all(action='DESELECT')
    obj1.select_set(True)
    bpy.context.view_layer.objects.active = obj1
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.empty_display_type = 'ARROWS'
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj1
    constraint.rigid_body_constraint.object2 = obj2
    constraint.rigid_body_constraint.use_breaking = True
    constraint.rigid_body_constraint.breaking_threshold = 10000
    constraint.location = pivot_world

# Left leg to beam (top)
create_fixed_constraint(left_leg, beam, left_leg_top)
# Left leg to ground (bottom)
create_fixed_constraint(left_leg, ground, left_leg_bottom)
# Right leg to beam (top)
create_fixed_constraint(right_leg, beam, right_leg_top)
# Right leg to ground (bottom)
create_fixed_constraint(right_leg, ground, right_leg_bottom)

# Set collision margins for stability
for obj in [ground, beam, left_leg, right_leg, load]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

print("Asymmetric A-frame structure created. Run simulation for", simulation_frames, "frames.")