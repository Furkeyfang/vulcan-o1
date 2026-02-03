import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 3.0, 0.5)
chassis_loc = (0.0, 0.0, 0.0)
wheel_radius = 0.5
wheel_depth = 0.2
wheel_z = -0.35
front_wheel_loc = (0.0, 1.5, wheel_z)
rear_wheel_loc = (0.0, -1.5, wheel_z)
ground_z = -1.0
front_motor_velocity = 2.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, ground_z))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 5.0  # kg
chassis.rigid_body.friction = 1.0
chassis.rigid_body.use_margin = True
chassis.rigid_body.collision_margin = 0.001

# Create front wheel (cylinder, rotated for Y-axis hinge)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_radius,
    depth=wheel_depth,
    location=front_wheel_loc
)
front_wheel = bpy.context.active_object
front_wheel.rotation_euler = (math.radians(90), 0, 0)  # Axis along Y
bpy.ops.rigidbody.object_add()
front_wheel.rigid_body.mass = 1.0
front_wheel.rigid_body.friction = 1.0

# Create rear wheel (cylinder, rotated for X-axis hinge)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_radius,
    depth=wheel_depth,
    location=rear_wheel_loc
)
rear_wheel = bpy.context.active_object
rear_wheel.rotation_euler = (0, math.radians(90), 0)  # Axis along X
bpy.ops.rigidbody.object_add()
rear_wheel.rigid_body.mass = 1.0
rear_wheel.rigid_body.friction = 1.0

# Add hinge constraints
bpy.ops.rigidbody.constraint_add(type='HINGE')
front_hinge = bpy.context.active_object
front_hinge.name = "Front_Hinge"
front_hinge.rigid_body_constraint.object1 = chassis
front_hinge.rigid_body_constraint.object2 = front_wheel
front_hinge.location = front_wheel_loc
front_hinge.rigid_body_constraint.pivot_type = 'CENTER'
front_hinge.rigid_body_constraint.use_angular_friction = True
front_hinge.rigid_body_constraint.angular_friction = 0.1
front_hinge.rigid_body_constraint.use_limit_ang_z = False
front_hinge.rigid_body_constraint.use_motor_ang = True
front_hinge.rigid_body_constraint.motor_ang_target_velocity = front_motor_velocity
front_hinge.rigid_body_constraint.motor_ang_max_impulse = 5.0

bpy.ops.rigidbody.constraint_add(type='HINGE')
rear_hinge = bpy.context.active_object
rear_hinge.name = "Rear_Hinge"
rear_hinge.rigid_body_constraint.object1 = chassis
rear_hinge.rigid_body_constraint.object2 = rear_wheel
rear_hinge.location = rear_wheel_loc
rear_hinge.rigid_body_constraint.pivot_type = 'CENTER'
rear_hinge.rigid_body_constraint.use_angular_friction = True
rear_hinge.rigid_body_constraint.angular_friction = 0.1
rear_hinge.rigid_body_constraint.use_limit_ang_z = False

# Set up simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250

# Keyframe initial state
chassis.keyframe_insert(data_path="rotation_euler", frame=1)
front_wheel.keyframe_insert(data_path="rotation_euler", frame=1)
rear_wheel.keyframe_insert(data_path="rotation_euler", frame=1)

# Verification setup (optional: add marker to track rotation)
bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0.5))
marker = bpy.context.active_object
marker.parent = chassis