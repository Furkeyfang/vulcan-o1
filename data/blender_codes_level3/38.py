import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.2)
wheel_rad = 0.4
wheel_dep = 0.15
wheel_z = 0.4
front_x = 1.0
rear_x = -1.0
left_y = -1.15
right_y = 1.15
motor_vel = 5.0
ground_sz = 20.0

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_sz, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (cube)
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 5.0
chassis.rigid_body.collision_shape = 'BOX'

# Wheel creation function
def create_wheel(name, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_rad,
        depth=wheel_dep,
        location=location,
        rotation=(0, math.pi/2, 0)  # Orient cylinder axis along X
    )
    wheel = bpy.context.active_object
    wheel.name = name
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = 0.5
    wheel.rigid_body.collision_shape = 'CYLINDER'
    return wheel

# Create four wheels
wheels = []
wheel_positions = [
    (front_x, left_y, wheel_z),   # Left front
    (rear_x, left_y, wheel_z),    # Left rear
    (front_x, right_y, wheel_z),  # Right front
    (rear_x, right_y, wheel_z)    # Right rear
]
names = ['wheel_lf', 'wheel_lr', 'wheel_rf', 'wheel_rr']
for i, pos in enumerate(wheel_positions):
    wheel = create_wheel(names[i], pos)
    wheels.append(wheel)

# Create hinge constraints with motors
for wheel in wheels:
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel.location)
    constraint_obj = bpy.context.active_object
    constraint_obj.name = f"hinge_{wheel.name}"
    
    # Setup rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_obj.rigid_body_constraint
    constraint.type = 'HINGE'
    constraint.object1 = chassis
    constraint.object2 = wheel
    constraint.use_global_axis = True
    constraint.axis = 'X'  # Rotation around X-axis
    
    # Motor settings
    constraint.use_motor = True
    constraint.motor_velocity = motor_vel
    constraint.motor_max_impulse = 10.0

# Configure simulation
bpy.context.scene.frame_end = 300
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = 300

# Bake simulation (headless compatible)
print("Baking physics simulation...")
bpy.ops.ptcache.bake_all(bake=True)

# Verify final position
bpy.context.scene.frame_set(300)
final_pos = chassis.location
print(f"Rover final position: {final_pos}")
print(f"Target (0,0,15), Distance: {final_pos.length}")