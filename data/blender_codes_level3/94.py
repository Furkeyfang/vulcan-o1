import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
chassis_dim = (3.0, 1.5, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
wheel_radius = 0.4
wheel_depth = 0.15
axle_radius = 0.05
axle_length = 1.8
left_axle_loc = (0.0, -0.75, 0.4)
right_axle_loc = (0.0, 0.75, 0.4)
left_wheel1_loc = (0.0, -1.65, 0.4)
left_wheel2_loc = (0.0, 0.15, 0.4)
right_wheel1_loc = (0.0, -0.15, 0.4)
right_wheel2_loc = (0.0, 1.65, 0.4)
motor_velocity = 4.0
turn_velocity = -4.0
frame_count = 50
fps = 60

# Set scene properties
scene = bpy.context.scene
scene.frame_end = frame_count
scene.render.fps = fps

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (cube aligned with world axes)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.collision_shape = 'BOX'

# Helper function to create Y-aligned cylinder
def create_y_cylinder(name, location, radius, length):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=radius,
        depth=2.0,  # Default Blender cylinder height
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = (math.pi/2, 0, 0)  # Rotate 90° around X to align with Y
    obj.scale = (1, length/2, 1)  # Scale Y to desired length
    return obj

# Create left axle
left_axle = create_y_cylinder("Left_Axle", left_axle_loc, axle_radius, axle_length)
bpy.ops.rigidbody.object_add()

# Create right axle
right_axle = create_y_cylinder("Right_Axle", right_axle_loc, axle_radius, axle_length)
bpy.ops.rigidbody.object_add()

# Create wheels (thin cylinders aligned with Y)
wheel_locs = [left_wheel1_loc, left_wheel2_loc, right_wheel1_loc, right_wheel2_loc]
wheel_names = ["Wheel_L1", "Wheel_L2", "Wheel_R1", "Wheel_R2"]
wheels = []

for i in range(4):
    wheel = create_y_cylinder(wheel_names[i], wheel_locs[i], wheel_radius, wheel_depth)
    bpy.ops.rigidbody.object_add()
    wheels.append(wheel)

# Create hinge constraints between chassis and axles
def add_hinge_motor(obj_a, obj_b, pivot, axis, motor_vel, name):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints["RigidBodyConstraint"]
    constraint.name = name
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.type = 'HINGE'
    constraint.pivot_type = 'CUSTOM'
    constraint.pivot_x = pivot[0]
    constraint.pivot_y = pivot[1]
    constraint.pivot_z = pivot[2]
    constraint.use_limit_ang_z = False
    constraint.use_motor_ang = True
    constraint.motor_ang_target_velocity = motor_vel
    constraint.motor_ang_max_impulse = 10.0

# Left hinge motor (forward during turn)
add_hinge_motor(
    chassis, left_axle,
    pivot=left_axle_loc,
    axis=(0, 1, 0),
    motor_vel=motor_velocity,
    name="Left_Hinge_Motor"
)

# Right hinge motor (reverse during turn)
add_hinge_motor(
    chassis, right_axle,
    pivot=right_axle_loc,
    axis=(0, 1, 0),
    motor_vel=turn_velocity,
    name="Right_Hinge_Motor"
)

# Create fixed constraints between axles and wheels
def add_fixed_constraint(obj_a, obj_b, name):
    bpy.ops.object.select_all(action='DESELECT')
    obj_a.select_set(True)
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    constraint = obj_a.constraints["RigidBodyConstraint"]
    constraint.name = name
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    constraint.type = 'FIXED'
    constraint.use_breaking = False

# Connect left wheels to left axle
add_fixed_constraint(left_axle, wheels[0], "Fix_L1")
add_fixed_constraint(left_axle, wheels[1], "Fix_L2")

# Connect right wheels to right axle
add_fixed_constraint(right_axle, wheels[2], "Fix_R1")
add_fixed_constraint(right_axle, wheels[3], "Fix_R2")

# Configure rigid body world
if scene.rigidbody_world is None:
    scene.rigidbody_world_create()
rb_world = scene.rigidbody_world
rb_world.time_scale = 1.0
rb_world.steps_per_second = 60
rb_world.solver_iterations = 50

print("Differential steering vehicle constructed successfully.")
print(f"Left motor: {motor_velocity} rad/s, Right motor: {turn_velocity} rad/s")
print(f"Simulation will run for {frame_count} frames ({frame_count/fps:.2f}s)")