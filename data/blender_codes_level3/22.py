import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 2.0, 0.5)
chassis_loc = (0.0, 0.0, 0.25)
block_dim = (2.0, 2.0, 1.0)
block_loc = (0.0, -1.5, 1.0)
wheel_depth = 0.15
rear_radius = 0.4
front_radius = 0.3
rear_right_loc = (1.575, -1.0, 0.4)
rear_left_loc = (-1.575, -1.0, 0.4)
front_right_loc = (1.575, 1.0, 0.3)
front_left_loc = (-1.575, 1.0, 0.3)
motor_velocity = 6.0

# Mass properties
chassis_mass = 1.0
block_mass = 5.0
rear_wheel_mass = 0.5
front_wheel_mass = 0.3

# Enable rigidbody world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Helper: Create wheel cylinder with X as axis
def create_wheel(name, radius, depth, location, mass):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.rotation_euler = (0, math.pi/2, 0)  # Rotate for X-axis rotation
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = mass
    wheel.rigid_body.friction = 0.8
    wheel.rigid_body.linear_damping = 0.05
    wheel.rigid_body.angular_damping = 0.05
    return wheel

# 1. Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.friction = 0.5

# 2. Create rear-heavy block
bpy.ops.mesh.primitive_cube_add(size=1.0, location=block_loc)
block = bpy.context.active_object
block.name = "RearBlock"
block.scale = block_dim
bpy.ops.rigidbody.object_add()
block.rigid_body.mass = block_mass

# 3. Fixed constraint between block and chassis
bpy.ops.rigidbody.constraint_add(type='FIXED')
constraint = bpy.context.active_object
constraint.name = "Block_Chassis_Fixed"
constraint.rigid_body_constraint.object1 = chassis
constraint.rigid_body_constraint.object2 = block
constraint.matrix_world = block.matrix_world

# 4. Create wheels
wheels = [
    create_wheel("RearWheel_Right", rear_radius, wheel_depth, rear_right_loc, rear_wheel_mass),
    create_wheel("RearWheel_Left", rear_radius, wheel_depth, rear_left_loc, rear_wheel_mass),
    create_wheel("FrontWheel_Right", front_radius, wheel_depth, front_right_loc, front_wheel_mass),
    create_wheel("FrontWheel_Left", front_radius, wheel_depth, front_left_loc, front_wheel_mass)
]

# 5. Add hinge constraints
motor_wheels = [wheels[0], wheels[1]]  # Rear wheels
for i, wheel in enumerate(wheels):
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    hinge = bpy.context.active_object
    hinge.name = f"Hinge_{wheel.name}"
    hinge.rigid_body_constraint.object1 = chassis
    hinge.rigid_body_constraint.object2 = wheel
    hinge.matrix_world = wheel.matrix_world  # Pivot at wheel center
    hinge.rigid_body_constraint.use_limit_z = False
    
    # Set motor for rear wheels
    if wheel in motor_wheels:
        hinge.rigid_body_constraint.use_motor_z = True
        hinge.rigid_body_constraint.motor_angular_target_velocity = motor_velocity
        hinge.rigid_body_constraint.motor_max_z_impulse = 2.0

# 6. Set initial location (already at (0,0,0) via chassis bottom)
# 7. Optional: Add ground plane
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 5, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'