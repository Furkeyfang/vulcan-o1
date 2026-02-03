import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.0)
column_rad = 0.1
column_height = 0.5
column_loc = (0.0, 1.0, 0.4)
wheel_rad = 0.3
wheel_depth = 0.05
wheel_loc = (0.0, 1.0, 0.675)
target_angles = [0.5236, -0.7854, 1.5708]
stiffness = 500.0
damping = 44.72
tolerance = 0.0349
frame_count = 50
solver_iters = 50
substeps = 10

# Configure rigid body world for precision
bpy.context.scene.rigidbody_world.substeps_per_frame = substeps
bpy.context.scene.rigidbody_world.solver_iterations = solver_iters

# 1. Create base platform (chassis)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Chassis"
base.scale = (base_dim[0]/2, base_dim[1]/2, base_dim[2]/2)  # Convert to Blender scale
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Create steering column
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=column_rad,
    depth=column_height,
    location=column_loc
)
column = bpy.context.active_object
column.name = "Steering_Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.collision_shape = 'CYLINDER'

# 3. Create steering wheel
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=wheel_rad,
    depth=wheel_depth,
    location=wheel_loc
)
wheel = bpy.context.active_object
wheel.name = "Steering_Wheel"
bpy.ops.rigidbody.object_add()
wheel.rigid_body.type = 'ACTIVE'
wheel.rigid_body.collision_shape = 'CYLINDER'

# Rotate wheel 90° around X-axis for correct orientation
wheel.rotation_euler = (math.radians(90), 0, 0)

# 4. Create Fixed constraint between base and column
bpy.ops.object.empty_add(type='PLAIN_AXES', location=column_loc)
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
fixed_constraint.rigid_body_constraint.type = 'FIXED'
fixed_constraint.rigid_body_constraint.object1 = base
fixed_constraint.rigid_body_constraint.object2 = column

# 5. Create Hinge constraint between column and wheel
bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel_loc)
hinge_constraint = bpy.context.active_object
hinge_constraint.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge_constraint.rigid_body_constraint.type = 'HINGE'
hinge_constraint.rigid_body_constraint.object1 = column
hinge_constraint.rigid_body_constraint.object2 = wheel
hinge_constraint.rigid_body_constraint.use_limit_ang_z = True
hinge_constraint.rigid_body_constraint.limit_ang_z_lower = -math.pi
hinge_constraint.rigid_body_constraint.limit_ang_z_upper = math.pi

# Configure servo motor
hinge_constraint.rigid_body_constraint.use_motor_ang_z = True
hinge_constraint.rigid_body_constraint.motor_ang_z_type = 'SERVO'
hinge_constraint.rigid_body_constraint.motor_ang_z_stiffness = stiffness
hinge_constraint.rigid_body_constraint.motor_ang_z_damping = damping
hinge_constraint.rigid_body_constraint.motor_ang_z_target_velocity = 0.0

# 6. Create visual target for verification
bpy.ops.mesh.primitive_cone_add(
    vertices=32,
    radius1=0.2,
    depth=0.5,
    location=(0.0, 6.0, 0.675)
)
target = bpy.context.active_object
target.name = "Target"
target.rotation_euler = (math.radians(90), 0, 0)

# 7. Keyframe servo target angles
for i, angle in enumerate(target_angles):
    frame = (i + 1) * 20  # Frames 20, 40, 60
    hinge_constraint.rigid_body_constraint.motor_ang_z_servo_target = angle
    hinge_constraint.rigid_body_constraint.keyframe_insert(
        data_path='motor_ang_z_servo_target',
        frame=frame
    )

# Set animation range for verification
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100