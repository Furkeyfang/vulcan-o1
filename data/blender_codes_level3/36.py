import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (5.0, 3.0, 0.5)
chassis_loc = (0.0, 0.0, 0.0)

wheel_radius = 0.6
wheel_depth = 0.25
wheel_positions = [
    (-2.5, -1.5, -0.25),
    (-2.5,  1.5, -0.25),
    ( 2.5, -1.5, -0.25),
    ( 2.5,  1.5, -0.25)
]

ground_z = -0.85
ground_scale = (20.0, 20.0, 1.0)

box_dim = (2.0, 2.0, 1.0)
box_loc = (0.0, 0.0, 0.75)

motor_velocity = 3.5

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, ground_z))
ground = bpy.context.active_object
ground.scale = ground_scale
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'

# Create wheels
wheels = []
for pos in wheel_positions:
    # Cylinder: default axis along Z, depth along Z
    bpy.ops.mesh.primitive_cylinder_add(radius=wheel_radius, depth=wheel_depth, location=pos)
    wheel = bpy.context.active_object
    # Rotate 90° around Y so cylinder axis aligns with X (for hinge along X)
    wheel.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheels.append(wheel)

# Create load box
bpy.ops.mesh.primitive_cube_add(size=1, location=box_loc)
box = bpy.context.active_object
box.scale = box_dim
bpy.ops.rigidbody.object_add()
box.rigid_body.type = 'ACTIVE'

# Create constraints
for wheel in wheels:
    # Add hinge constraint between wheel and chassis
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    constraint = bpy.context.active_object
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    # Set pivot at wheel center (already in world coordinates)
    constraint.location = wheel.location
    # Align axis to X (global)
    constraint.rigid_body_constraint.axis = 'X'
    # Enable motor
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_velocity = motor_velocity

# Fixed constraint between load box and chassis
bpy.ops.rigidbody.constraint_add(type='FIXED')
fixed_constraint = bpy.context.active_object
fixed_constraint.rigid_body_constraint.object1 = chassis
fixed_constraint.rigid_body_constraint.object2 = box
fixed_constraint.location = chassis_loc