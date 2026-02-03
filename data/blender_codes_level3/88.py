import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
chassis_dim = (3.0, 1.0, 0.3)
chassis_loc = (0.0, 0.0, 0.3)
axle_dim = (0.1, 0.8, 0.1)
front_axle_loc = (0.0, 0.4, 0.15)
rear_axle_loc = (0.0, -0.4, 0.15)
wheel_radius = 0.25
wheel_depth = 0.15
front_wheel_left_loc = (0.5, 0.0, 0.25)
front_wheel_right_loc = (0.5, 0.8, 0.25)
rear_wheel_left_loc = (-0.5, -0.8, 0.25)
rear_wheel_right_loc = (-0.5, 0.0, 0.25)
steering_motor_velocity = 1.0
steering_motor_max_torque = 10.0
chassis_mass = 50.0
axle_mass = 5.0
wheel_mass = 3.0

# Helper function to create cylinder aligned along Y (for axle)
def create_cylinder_along_y(location, dimensions, name):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=dimensions[0]/2,
        depth=dimensions[1],
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    # Rotate 90° around X to align length along Y
    obj.rotation_euler = (math.radians(90), 0, 0)
    return obj

# Helper to create wheel (cylinder along Y, but depth is along Y)
def create_wheel(location, name):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    # Rotate 90° around X so cylinder axis is Y (for rolling)
    obj.rotation_euler = (math.radians(90), 0, 0)
    return obj

# 1. Create Chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.collision_shape = 'BOX'

# 2. Create Front Axle
front_axle = create_cylinder_along_y(front_axle_loc, axle_dim, "Front_Axle")
bpy.ops.rigidbody.object_add()
front_axle.rigid_body.mass = axle_mass
front_axle.rigid_body.collision_shape = 'CYLINDER'

# 3. Create Rear Axle
rear_axle = create_cylinder_along_y(rear_axle_loc, axle_dim, "Rear_Axle")
bpy.ops.rigidbody.object_add()
rear_axle.rigid_body.mass = axle_mass
rear_axle.rigid_body.collision_shape = 'CYLINDER'

# 4. Create Wheels
wheels = []
wheel_locs = [front_wheel_left_loc, front_wheel_right_loc, rear_wheel_left_loc, rear_wheel_right_loc]
wheel_names = ["Front_Wheel_Left", "Front_Wheel_Right", "Rear_Wheel_Left", "Rear_Wheel_Right"]
for loc, name in zip(wheel_locs, wheel_names):
    wheel = create_wheel(loc, name)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheels.append(wheel)

# 5. Add Hinge Constraints for Steering (Chassis-Axle)
def add_steering_hinge(axle, motor_velocity, motor_torque):
    # Create empty object as constraint pivot at axle location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=axle.location)
    pivot = bpy.context.active_object
    pivot.name = axle.name + "_Steering_Pivot"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = axle.name + "_Steering_Hinge"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = axle
    constraint.rigid_body_constraint.use_limit_ang_z = False
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_ang_max_torque = motor_torque
    # Set pivot location
    constraint.location = axle.location

# Front axle steers clockwise, rear counterclockwise for coordinated turn
add_steering_hinge(front_axle, steering_motor_velocity, steering_motor_max_torque)
add_steering_hinge(rear_axle, -steering_motor_velocity, steering_motor_max_torque)

# 6. Add Hinge Constraints for Rolling (Axle-Wheel) and parent wheels to axles
# Determine which wheel belongs to which axle by Y position
front_wheels = [w for w in wheels if "Front" in w.name]
rear_wheels = [w for w in wheels if "Rear" in w.name]

for wheel in front_wheels:
    wheel.parent = front_axle
for wheel in rear_wheels:
    wheel.parent = rear_axle

# Add rolling hinge constraints (free rotation around local Y)
for wheel in wheels:
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = wheel.name + "_Rolling_Hinge"
    constraint.rigid_body_constraint.type = 'HINGE'
    # Constraint between axle and wheel
    if wheel in front_wheels:
        constraint.rigid_body_constraint.object1 = front_axle
    else:
        constraint.rigid_body_constraint.object1 = rear_axle
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_limit_ang_z = False  # Free rotation
    constraint.rigid_body_constraint.use_motor_ang = False
    # Set axis to local Y (rolling axis) - in Blender hinge uses local Z by default, so adjust
    # We'll set the constraint's rotation to align local Z with wheel's local Y
    # Wheel's local Y is its cylinder axis (after 90° X rotation). So we need to rotate constraint 90° around X relative to wheel.
    # Instead, we can set constraint to use world Y? Actually, we want wheel to rotate around its own Y axis, which moves with steering.
    # So we set constraint space to local and axis to (0,1,0) in wheel's local space.
    constraint.rigid_body_constraint.use_breaking = False
    # Note: In Blender, hinge constraint axis is fixed to local Z of the constraint object. We'll align constraint object with wheel's local Y.
    constraint.rotation_euler = wheel.rotation_euler @ mathutils.Euler((math.radians(90), 0, 0), 'XYZ')
    constraint.location = wheel.location

# 7. Set collision margins and damping for stability
for obj in [chassis, front_axle, rear_axle] + wheels:
    obj.rigid_body.collision_margin = 0.01
    obj.rigid_body.linear_damping = 0.04
    obj.rigid_body.angular_damping = 0.1

print("Vehicle with dual-axle steering constructed. Steering motors activated.")