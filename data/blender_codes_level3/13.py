import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
c_dim = (3.0, 1.5, 0.4)
c_loc = (0.0, 0.0, 0.2)
w_rad = 0.6
w_dep = 0.3
w_left = (-1.5, 0.6, 0.6)
w_right = (-1.5, -0.6, 0.6)
cube_dim = (1.0, 1.0, 1.0)
cube_loc = (2.5, 0.0, 0.5)
mot_vel = 3.0
mot_torque = 1000.0
g_dim = (20.0, 20.0, 0.2)
g_loc = (0.0, 0.0, -0.1)

# Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_cube_add(size=1, location=g_loc)
ground = bpy.context.active_object
ground.scale = (g_dim[0], g_dim[1], g_dim[2])
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.name = "Ground"

# Create chassis platform
bpy.ops.mesh.primitive_cube_add(size=1, location=c_loc)
chassis = bpy.context.active_object
chassis.scale = (c_dim[0]/2, c_dim[1]/2, c_dim[2]/2)  # Blender cube default size=2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.collision_shape = 'BOX'
chassis.name = "Chassis"

# Function to create wheel with proper cylinder orientation
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=w_rad,
        depth=w_dep,
        location=location,
        rotation=(0, 0, math.pi/2)  # Rotate 90° around Z so cylinder axis aligns with Y
    )
    wheel = bpy.context.active_object
    wheel.name = name
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    return wheel

# Create left and right wheels
wheel_L = create_wheel("Wheel_Left", w_left)
wheel_R = create_wheel("Wheel_Right", w_right)

# Function to create hinge constraint between chassis and wheel
def create_motor_hinge(chassis_obj, wheel_obj, pivot_location):
    # Create empty object at pivot (headless compatible method)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_location)
    pivot = bpy.context.active_object
    pivot.name = wheel_obj.name + "_Pivot"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = wheel_obj.name + "_Hinge"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis_obj
    constraint.rigid_body_constraint.object2 = wheel_obj
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_ang_vel = mot_vel
    constraint.rigid_body_constraint.motor_max_torque = mot_torque
    constraint.rigid_body_constraint.use_limit_lin_x = True
    constraint.rigid_body_constraint.use_limit_lin_y = True
    constraint.rigid_body_constraint.use_limit_lin_z = True
    constraint.rigid_body_constraint.use_limit_ang_x = False
    constraint.rigid_body_constraint.use_limit_ang_y = False
    constraint.rigid_body_constraint.use_limit_ang_z = True
    constraint.rigid_body_constraint.limit_ang_z_lower = -0.01
    constraint.rigid_body_constraint.limit_ang_z_upper = 0.01
    
    # Set pivot to wheel center (constraint location already at pivot)
    constraint.location = pivot_location
    # Parent constraint to pivot for organization (optional)
    constraint.parent = pivot
    return constraint

# Create motorized hinges
create_motor_hinge(chassis, wheel_L, w_left)
create_motor_hinge(chassis, wheel_R, w_right)

# Create passive cube
bpy.ops.mesh.primitive_cube_add(size=1, location=cube_loc)
cube = bpy.context.active_object
cube.scale = (cube_dim[0]/2, cube_dim[1]/2, cube_dim[2]/2)
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'PASSIVE'
cube.rigid_body.collision_shape = 'BOX'
cube.name = "Passive_Cube"

# Set up basic scene physics (headless compatible)
scene = bpy.context.scene
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 10
scene.frame_end = 300  # Verification requirement

# Ensure all objects have proper collision margins
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04