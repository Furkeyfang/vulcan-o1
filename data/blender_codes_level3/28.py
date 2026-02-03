import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (5.0, 3.0, 0.6)
chassis_loc = (0.0, 0.0, 0.9)
wheel_radius = 0.6
wheel_depth = 0.25
wheel_z = 0.6
front_x = 2.375
rear_x = -2.375
left_y = 1.5
right_y = -1.5
block_dim = (1.5, 1.5, 1.5)
block_loc = (4.25, 0.0, 0.75)
motor_velocity = 2.5
sim_frames = 500
chassis_mass = 200.0
wheel_mass = 20.0
block_mass = 100.0

# Enable physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.collision_shape = 'BOX'
chassis.rigid_body.friction = 0.8

# Wheel creation function
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location,
        rotation=(0, 0.5*3.14159, 0)  # Rotate 90° around Y for X-axis alignment
    )
    wheel = bpy.context.active_object
    wheel.name = name
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.friction = 1.2
    return wheel

# Create four wheels
wheels = []
wheel_positions = [
    (front_x, left_y, wheel_z, "FL"),
    (front_x, right_y, wheel_z, "FR"),
    (rear_x, left_y, wheel_z, "RL"),
    (rear_x, right_y, wheel_z, "RR")
]
for x, y, z, suffix in wheel_positions:
    wheel = create_wheel(f"Wheel_{suffix}", (x, y, z))
    wheels.append(wheel)

# Create hinge constraints
for wheel in wheels:
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{wheel.name}"
    constraint_empty.empty_display_size = 0.3
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint_empty.rigid_body_constraint
    rb_constraint.type = 'HINGE'
    rb_constraint.object1 = chassis
    rb_constraint.object2 = wheel
    rb_constraint.use_limit_ang_z = True
    rb_constraint.limit_ang_z_lower = -3.14159
    rb_constraint.limit_ang_z_upper = 3.14159
    rb_constraint.use_motor_ang = True
    rb_constraint.motor_ang_velocity = motor_velocity
    rb_constraint.motor_ang_max_torque = 500.0

# Create block
bpy.ops.mesh.primitive_cube_add(size=1, location=block_loc)
block = bpy.context.active_object
block.scale = (block_dim[0]/2, block_dim[1]/2, block_dim[2]/2)
bpy.ops.rigidbody.object_add()
block.rigid_body.type = 'ACTIVE'
block.rigid_body.mass = block_mass
block.rigid_body.collision_shape = 'BOX'
block.rigid_body.friction = 0.5

# Set simulation range
bpy.context.scene.frame_end = sim_frames

# Bake physics simulation
if bpy.context.scene.rigidbody_world.point_cache.is_baked is False:
    bpy.ops.ptcache.bake_all(bake=True)