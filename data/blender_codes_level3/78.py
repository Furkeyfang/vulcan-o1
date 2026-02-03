import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Define parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.4)
wheel_radius = 0.3
wheel_depth = 0.15
front_wheel_y = 0.75
rear_wheel_y = -0.75
wheel_x = 1.2
wheel_z = 0.3
steer_limit = 0.5235987756  # ±30° in radians
target_steer = -0.5235987756  # -30° in radians
simulation_frames = 100

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.collision_shape = 'BOX'

# Wheel creation function
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate cylinder: default Z-axis becomes wheel axis, rotate 90° about X
    wheel.rotation_euler = (math.pi/2, 0, 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    return wheel

# Create wheels
wheel_fl = create_wheel("Wheel_FL", (-wheel_x, front_wheel_y, wheel_z))
wheel_fr = create_wheel("Wheel_FR", (wheel_x, front_wheel_y, wheel_z))
wheel_rl = create_wheel("Wheel_RL", (-wheel_x, rear_wheel_y, wheel_z))
wheel_rr = create_wheel("Wheel_RR", (wheel_x, rear_wheel_y, wheel_z))

# Constraint creation function
def create_constraint(name, obj_a, obj_b, location, ctype, limits=None, motor_target=None):
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    empty.empty_display_size = 0.2
    
    # Add constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object.rigid_body_constraint
    constraint.type = ctype
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    # Set limits for hinge
    if limits and ctype == 'HINGE':
        constraint.use_limit_ang_z = True
        constraint.limit_ang_z_lower = -limits
        constraint.limit_ang_z_upper = limits
    
    # Set motor
    if motor_target is not None and ctype == 'HINGE':
        constraint.use_motor_ang_z = True
        constraint.motor_ang_z_target_velocity = 0.0  # Position control via target angle
        constraint.motor_ang_z_target_position = motor_target
        constraint.motor_ang_z_max_impulse = 10.0  # Sufficient torque
    
    return constraint

# Create constraints
create_constraint("Hinge_FL", chassis, wheel_fl, wheel_fl.location, 
                  'HINGE', limits=steer_limit, motor_target=target_steer)
create_constraint("Hinge_FR", chassis, wheel_fr, wheel_fr.location, 
                  'HINGE', limits=steer_limit, motor_target=target_steer)
create_constraint("Fixed_RL", chassis, wheel_rl, wheel_rl.location, 'FIXED')
create_constraint("Fixed_RR", chassis, wheel_rr, wheel_rr.location, 'FIXED')

# Set simulation parameters
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Record initial heading
initial_rotation = chassis.rotation_euler.z

# Run simulation
for frame in range(simulation_frames):
    bpy.context.scene.frame_set(frame)
    # Enable motors only after first frame to allow settling
    if frame > 0:
        for obj in bpy.data.objects:
            if obj.rigid_body_constraint and obj.rigid_body_constraint.type == 'HINGE':
                obj.rigid_body_constraint.use_motor_ang_z = True

# Calculate heading change
final_rotation = chassis.rotation_euler.z
heading_change = abs(final_rotation - initial_rotation) * 180 / math.pi
print(f"Heading change: {heading_change:.1f}°")
print(f"Verification: {'PASS' if heading_change > 30 else 'FAIL'}")

# Optional: Save final state for inspection
bpy.context.scene.frame_set(simulation_frames)