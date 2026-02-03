import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.2)
wheel_radius = 0.4
wheel_depth = 0.15
wheel_gap = 0.8
y_left = -wheel_gap / 2.0
y_right = wheel_gap / 2.0
wheel_clearance = 0.2
x_front = chassis_dim[0] / 2.0 - wheel_clearance
x_back = -chassis_dim[0] / 2.0 + wheel_clearance
wheel_z = wheel_radius
motor_velocity_left = 1.5
motor_velocity_right = -1.5
simulation_frames = 300
ground_size = 20.0

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = (chassis_dim[0]/2.0, chassis_dim[1]/2.0, chassis_dim[2]/2.0)  # Blender cube is 2x2x2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 10.0  # Reasonable mass for stability

# Helper to create a wheel and hinge
def create_wheel(name, location, motor_velocity):
    # Create cylinder (default axis Z)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=location)
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° around Y so cylinder axis aligns with X (hinge axis)
    wheel.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 2.0
    
    # Create hinge constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    hinge = bpy.context.active_object
    hinge.name = name + "_Hinge"
    hinge.empty_display_size = 0.5
    
    # Set constraint properties
    bpy.ops.rigidbody.constraint_add()
    hinge.rigid_body_constraint.type = 'HINGE'
    hinge.rigid_body_constraint.object1 = chassis
    hinge.rigid_body_constraint.object2 = wheel
    hinge.rigid_body_constraint.use_limit_ang_z = True
    hinge.rigid_body_constraint.limit_ang_z_lower = 0
    hinge.rigid_body_constraint.limit_ang_z_upper = 0  # Lock other rotations
    # Enable motor
    hinge.rigid_body_constraint.use_motor_ang = True
    hinge.rigid_body_constraint.motor_ang_velocity = motor_velocity
    hinge.rigid_body_constraint.motor_ang_max_impulse = 5.0  # Sufficient torque

# Create four wheels
create_wheel("Left_Front_Wheel", (x_front, y_left, wheel_z), motor_velocity_left)
create_wheel("Left_Back_Wheel", (x_back, y_left, wheel_z), motor_velocity_left)
create_wheel("Right_Front_Wheel", (x_front, y_right, wheel_z), motor_velocity_right)
create_wheel("Right_Back_Wheel", (x_back, y_right, wheel_z), motor_velocity_right)

# Set simulation length
bpy.context.scene.frame_end = simulation_frames

# Optional: Set gravity and simulation substeps for smoother motion
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Differential-drive rover constructed. Run simulation for", simulation_frames, "frames.")