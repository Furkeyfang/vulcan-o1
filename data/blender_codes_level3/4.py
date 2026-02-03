import bpy
import math
from mathutils import Matrix

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 2.0, 0.4)
chassis_loc = (0.0, 0.0, 0.2)
wheel_radius = 0.4
wheel_depth = 0.15
left_wheel_loc = (-0.5, 0.0, 0.2)
right_wheel_loc = (0.5, 0.0, 0.2)
left_motor_vel = 5.0
right_motor_vel = 3.0
simulation_frames = 250
frame_rate = 60.0

# Set scene for physics simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.render.fps = int(frame_rate)

# Create chassis (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Blender cube radius
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'
chassis.rigid_body.collision_shape = 'BOX'

# Function to create wheel with hinge constraint
def create_wheel(name, location, motor_velocity):
    # Create cylinder (aligned along Z by default)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    
    # Rotate 90° around X so cylinder axis aligns with Y (hinge axis)
    wheel.rotation_euler = (math.radians(90), 0, 0)
    
    # Apply rigid body (active)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.angular_damping = 0.1  # Prevent overspin
    
    # Add hinge constraint between chassis and wheel
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"{name}_Hinge"
    constraint.empty_display_type = 'SINGLE_ARROW'
    
    # Configure constraint
    cons = constraint.rigid_body_constraint
    cons.type = 'HINGE'
    cons.object1 = chassis
    cons.object2 = wheel
    cons.pivot_type = 'CENTER'
    cons.use_angular_limit = True
    cons.limit_ang_z_lower = 0
    cons.limit_ang_z_upper = 0  # Lock other axes
    
    # Position constraint at wheel center
    constraint.location = location
    
    # Set motor parameters
    cons.use_motor_ang = True
    cons.motor_ang_target_velocity = motor_velocity
    cons.motor_ang_max_impulse = 10.0  # Sufficient torque
    
    return wheel, constraint

# Create left wheel (faster motor)
left_wheel, left_hinge = create_wheel("Left_Wheel", left_wheel_loc, left_motor_vel)

# Create right wheel (slower motor)
right_wheel, right_hinge = create_wheel("Right_Wheel", right_wheel_loc, right_motor_vel)

# Set up ground plane for traction
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Configure physics world
bpy.context.scene.rigidbody_world.steps_per_second = int(frame_rate)
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Verification setup: Add text output for final position
bpy.ops.object.text_add(location=(0, 0, 2))
text_obj = bpy.context.active_object
text_obj.name = "Position_Display"
text_obj.data.body = "Final X: "
text_obj.scale = (0.2, 0.2, 0.2)

# Create driver to display chassis X position at frame 250
driver = text_obj.data.driver_add("body").driver
driver.type = 'SCRIPTED'
driver.expression = "'Final X: ' + str(round(chassis.location.x, 3))"

var = driver.variables.new()
var.name = "chassis"
var.type = 'TRANSFORMS'
target = var.targets[0]
target.id = chassis
target.transform_type = 'LOC_X'

# Animate motor activation at frame 1
bpy.context.scene.frame_set(1)
for hinge in [left_hinge, right_hinge]:
    hinge.rigid_body_constraint.motor_ang_target_velocity = 0
    hinge.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity")

bpy.context.scene.frame_set(5)
for hinge in [left_hinge, right_hinge]:
    hinge.rigid_body_constraint.motor_ang_target_velocity = hinge.rigid_body_constraint.motor_ang_target_velocity
    hinge.rigid_body_constraint.keyframe_insert(data_path="motor_ang_target_velocity")

print("Differential-drive robot constructed. Run simulation for 250 frames.")
print(f"Expected behavior: Curves right due to velocity differential (L:{left_motor_vel} vs R:{right_motor_vel} rad/s)")
print(f"Chassis should achieve X > 3.0m within {simulation_frames} frames")