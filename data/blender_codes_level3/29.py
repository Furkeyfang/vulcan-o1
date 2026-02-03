import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.4)
wheel_radius = 0.3
wheel_depth = 0.15
wheels_per_track = 6
track_spacing = 0.3
left_track_x = -1.05
right_track_x = 1.05
wheel_z = 0.3
wheel_y_start = -0.75
hinge_axis = (1.0, 0.0, 0.0)
motor_velocity = 6.0
simulation_frames = 300
target_y = 7.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'

# Function to create wheel and constraint
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate cylinder to align with X-axis (default cylinder is Z-up)
    wheel.rotation_euler = (0, math.pi/2, 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.friction = 1.0
    
    # Create hinge constraint between wheel and chassis
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{name}"
    constraint.empty_display_type = 'ARROWS'
    constraint.location = location
    cons = constraint.rigid_body_constraint
    cons.type = 'HINGE'
    cons.object1 = chassis
    cons.object2 = wheel
    cons.use_override_solver_iterations = True
    cons.solver_iterations = 50
    cons.use_limit_ang_z = True
    cons.limit_ang_z_lower = 0
    cons.limit_ang_z_upper = 0
    cons.use_motor_ang_z = True
    cons.motor_ang_z_velocity = motor_velocity
    cons.motor_ang_z_max_torque = 100.0
    # Set hinge axis in world coordinates (X-axis)
    cons.pivot_type = 'BODY_AXIS'
    cons.axis_x = hinge_axis[0]
    cons.axis_y = hinge_axis[1]
    cons.axis_z = hinge_axis[2]
    return wheel

# Create left track wheels
for i in range(wheels_per_track):
    y_pos = wheel_y_start + i * track_spacing
    create_wheel(f"Left_Wheel_{i}", (left_track_x, y_pos, wheel_z))

# Create right track wheels
for i in range(wheels_per_track):
    y_pos = wheel_y_start + i * track_spacing
    create_wheel(f"Right_Wheel_{i}", (right_track_x, y_pos, wheel_z))

# Set simulation parameters
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Run simulation (headless rendering not required for physics)
# We'll advance frames programmatically
for frame in range(1, simulation_frames + 1):
    bpy.context.scene.frame_set(frame)

# Verification
final_y = chassis.location.y
print(f"Final Y position: {final_y}")
if final_y >= target_y:
    print("SUCCESS: Rover reached target distance")
else:
    print("FAIL: Rover did not reach target distance")