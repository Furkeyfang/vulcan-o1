import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 2.0, 0.4)
chassis_loc = (0.0, 0.0, 0.2)
wheel_radius = 0.4
wheel_depth = 0.15
wheel_offset = wheel_depth/2 + 0.05  # Half-depth plus clearance

# Calculate wheel positions
wheel_positions = [
    (chassis_dim[0]/2 - wheel_offset, chassis_dim[1]/2 - wheel_offset, wheel_radius),
    (chassis_dim[0]/2 - wheel_offset, -chassis_dim[1]/2 + wheel_offset, wheel_radius),
    (-chassis_dim[0]/2 + wheel_offset, chassis_dim[1]/2 - wheel_offset, wheel_radius),
    (-chassis_dim[0]/2 + wheel_offset, -chassis_dim[1]/2 + wheel_offset, wheel_radius)
]

hinge_axis = (1.0, 0.0, 0.0)  # X-axis rotation
motor_velocity = 3.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'
chassis.rigid_body.collision_shape = 'BOX'

# Function to create modular wheel assembly
def create_wheel(name, location):
    # Create wheel cylinder (oriented with axis along Y)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location,
        rotation=(0, 0, 0)
    )
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.rotation_euler = (0, 0, 0)  # Ensure proper orientation
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 2.0
    wheel.rigid_body.collision_shape = 'CYLINDER'
    
    # Create hinge constraint empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"{name}_Hinge"
    constraint_empty.empty_display_size = 0.5
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = chassis
    constraint.object2 = wheel
    constraint.use_limit_ang_z = False  # Free rotation
    constraint.use_motor_ang = True
    constraint.motor_ang_target_velocity = motor_velocity
    constraint.use_breaking = False
    
    return wheel, constraint_empty

# Create all four wheels
wheels = []
constraints = []
wheel_names = ["FR_Wheel", "FL_Wheel", "RR_Wheel", "RL_Wheel"]

for i, pos in enumerate(wheel_positions):
    wheel_obj, constraint_obj = create_wheel(wheel_names[i], pos)
    wheels.append(wheel_obj)
    constraints.append(constraint_obj)

# Set up simulation parameters
bpy.context.scene.frame_end = 300
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Set gravity to default (-9.8 Z)
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

# Verification setup (optional visualization)
print(f"Chassis created at {chassis.location}")
print(f"Target location: (5.0, 0.0, 0.0)")
print(f"Simulation will run for {bpy.context.scene.frame_end} frames")
print(f"Motor velocity: {motor_velocity} rad/s")

# To verify reaching target, you would need to run simulation and check position
# This would typically be done via Python script after simulation bake