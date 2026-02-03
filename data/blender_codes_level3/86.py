import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
axle_length = 2.0
axle_width = 0.2
axle_height = 0.2
axle_position = (0.0, 0.0, 0.5)

wheel_radius = 0.3
wheel_depth = 0.2
left_wheel_pos = (-1.0, 0.0, 0.7)
right_wheel_pos = (1.0, 0.0, 0.7)

hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 1.57  # rad/s

# Create axle beam (cuboid)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=axle_position)
axle = bpy.context.active_object
axle.name = "Axle_Beam"
axle.scale = (axle_length, axle_width, axle_height)

# Enable rigid body physics for axle
bpy.ops.rigidbody.object_add()
axle.rigid_body.type = 'ACTIVE'
axle.rigid_body.mass = 10.0
axle.rigid_body.friction = 0.5
axle.rigid_body.restitution = 0.1

# Create left wheel (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_radius,
    depth=wheel_depth,
    location=left_wheel_pos
)
left_wheel = bpy.context.active_object
left_wheel.name = "Left_Wheel"

# Enable rigid body physics for left wheel
bpy.ops.rigidbody.object_add()
left_wheel.rigid_body.type = 'ACTIVE'
left_wheel.rigid_body.mass = 2.0
left_wheel.rigid_body.friction = 0.8

# Create right wheel (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_radius,
    depth=wheel_depth,
    location=right_wheel_pos
)
right_wheel = bpy.context.active_object
right_wheel.name = "Right_Wheel"

# Enable rigid body physics for right wheel
bpy.ops.rigidbody.object_add()
right_wheel.rigid_body.type = 'ACTIVE'
right_wheel.rigid_body.mass = 2.0
right_wheel.rigid_body.friction = 0.8

# Create hinge constraints
# Left wheel hinge
bpy.ops.rigidbody.constraint_add()
left_hinge = bpy.context.active_object
left_hinge.name = "Left_Hinge"
left_hinge.rigid_body_constraint.type = 'HINGE'
left_hinge.rigid_body_constraint.object1 = axle
left_hinge.rigid_body_constraint.object2 = left_wheel
left_hinge.rigid_body_constraint.pivot_type = 'CENTER'
left_hinge.location = left_wheel_pos
left_hinge.rigid_body_constraint.use_limit_ang_z = False

# Enable motor for left hinge
left_hinge.rigid_body_constraint.use_motor_ang = True
left_hinge.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
left_hinge.rigid_body_constraint.motor_ang_max_torque = 5.0

# Right wheel hinge
bpy.ops.rigidbody.constraint_add()
right_hinge = bpy.context.active_object
right_hinge.name = "Right_Hinge"
right_hinge.rigid_body_constraint.type = 'HINGE'
right_hinge.rigid_body_constraint.object1 = axle
right_hinge.rigid_body_constraint.object2 = right_wheel
right_hinge.rigid_body_constraint.pivot_type = 'CENTER'
right_hinge.location = right_wheel_pos
right_hinge.rigid_body_constraint.use_limit_ang_z = False

# Enable motor for right hinge
right_hinge.rigid_body_constraint.use_motor_ang = True
right_hinge.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
right_hinge.rigid_body_constraint.motor_ang_max_torque = 5.0

# Create ground plane for reference
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Set rigid body world settings
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Steering axle assembly created successfully.")
print(f"Hinge motors set to {motor_velocity} rad/s angular velocity.")