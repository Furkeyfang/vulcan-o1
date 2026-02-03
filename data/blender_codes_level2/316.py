import bpy
import math

# 1. Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define variables from summary
R_inner = 6.0
R_outer = 9.0
depth = 3.0
thickness = 0.3
segment_width = 0.6
num_segments = 10
total_arc_angle = math.pi / 2.0
delta_theta = total_arc_angle / num_segments
wall_thickness = 0.5
wall_width = 6.0
wall_height = 3.0
wall_center = (0.0, 0.0, wall_height / 2.0)
load_force = -3433.5
concrete_density = 1000.0
solver_iterations = 50

# 3. Set up rigid body world
bpy.context.scene.rigidbody_world.solver_iterations = solver_iterations
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容

# 4. Create support wall
bpy.ops.mesh.primitive_cube_add(size=1.0, location=wall_center)
wall = bpy.context.active_object
wall.name = "SupportWall"
wall.scale = (wall_thickness, wall_width, wall_height)
bpy.ops.rigidbody.object_add()
wall.rigid_body.type = 'PASSIVE'
wall.rigid_body.mass = wall_thickness * wall_width * wall_height * concrete_density

# 5. Create platform segments
segments = []
for i in range(num_segments):
    theta = i * delta_theta
    # Centroid of segment box
    R_centroid = R_inner + depth / 2.0
    x = R_centroid * math.cos(theta)
    y = R_centroid * math.sin(theta)
    z = wall_height + thickness / 2.0  # on top of wall
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z))
    seg = bpy.context.active_object
    seg.name = f"Segment_{i}"
    # Scale: width (along arc), depth (radial), thickness (vertical)
    # We approximate the arc segment as a box with width = chord length at centroid radius.
    chord_width = 2.0 * R_centroid * math.sin(delta_theta / 2.0)
    seg.scale = (chord_width, depth, thickness)
    # Rotate the segment to align its local Y axis radially outward.
    seg.rotation_euler = (0.0, 0.0, theta)
    
    bpy.ops.rigidbody.object_add()
    seg.rigid_body.type = 'ACTIVE'
    seg.rigid_body.mass = chord_width * depth * thickness * concrete_density
    seg.rigid_body.collision_shape = 'BOX'
    seg.rigid_body.friction = 0.5
    seg.rigid_body.restitution = 0.0
    segments.append(seg)
    
    # Create Fixed Constraint between segment and wall at inner edge
    # Constraint location: inner edge point on the segment
    inner_x = R_inner * math.cos(theta)
    inner_y = R_inner * math.sin(theta)
    inner_z = wall_height  # top of wall, bottom of segment
    
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{i}"
    constraint.location = (inner_x, inner_y, inner_z)
    constraint.rigid_body_constraint.object1 = wall
    constraint.rigid_body_constraint.object2 = seg
    constraint.rigid_body_constraint.use_override_solver_iterations = True
    constraint.rigid_body_constraint.solver_iterations = 50

# 6. Apply load via Motor Constraint on last segment
last_seg = segments[-1]
# Load point: outer edge midpoint of last segment
theta_last = (num_segments - 1) * delta_theta + delta_theta / 2.0
load_x = R_outer * math.cos(theta_last)
load_y = R_outer * math.sin(theta_last)
load_z = wall_height  # same as inner edge (bottom of platform)

# Create an empty as target for motor constraint (optional, but makes pivot clear)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(load_x, load_y, load_z))
empty = bpy.context.active_object
empty.name = "LoadPoint"

# Motor constraint between last segment and empty (or world)
bpy.ops.rigidbody.constraint_add(type='MOTOR')
motor = bpy.context.active_object
motor.name = "LoadMotor"
motor.location = (load_x, load_y, load_z)
motor.rigid_body_constraint.object1 = last_seg
motor.rigid_body_constraint.object2 = empty  # could be None for world, but empty helps visualization
motor.rigid_body_constraint.motor_lin_target_velocity = 0.0  # we want force, not velocity
motor.rigid_body_constraint.use_motor_lin = True
motor.rigid_body_constraint.motor_lin_max_impulse = abs(load_force) / 60.0  # approximate impulse per frame (force * dt)
# Note: Motor constraint in Blender applies impulse to reach target velocity. 
# To simulate constant force, we'd need a script. This is an approximation.
# Alternatively, we can use a force field, but constraint is requested.
# We'll also enable limits to restrict motion to Z axis.
motor.rigid_body_constraint.limit_lin_x = True
motor.rigid_body_constraint.limit_lin_y = True
motor.rigid_body_constraint.limit_lin_z = False  # allow motion in Z under load
motor.rigid_body_constraint.limit_ang_x = True
motor.rigid_body_constraint.limit_ang_y = True
motor.rigid_body_constraint.limit_ang_z = True

# 7. Optional: Add a floor for visual reference (not necessary for simulation)
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, -0.1))
floor = bpy.context.active_object
floor.name = "Floor"
bpy.ops.rigidbody.object_add()
floor.rigid_body.type = 'PASSIVE'

print("Curved cantilever balcony constructed. Run simulation for 100 frames to test deflection.")