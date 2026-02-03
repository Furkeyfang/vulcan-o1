import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 1.5, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
wheel_radius = 0.25
wheel_depth = 0.15
wheel_positions = [
    (-1.25, -0.75, -0.15),
    (-1.25, 0.75, -0.15),
    (1.25, -0.75, -0.15),
    (1.25, 0.75, -0.15)
]
motor_velocity = 5.0
ground_size = 10.0
fixed_constraint_breaking_threshold = 1000.0
chassis_mass = 50.0
wheel_mass = 5.0

# Enable rigid body physics (if not already)
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Blender cube default size=2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.collision_shape = 'BOX'

# Create fixed constraint between chassis and ground
bpy.ops.object.empty_add(type='PLAIN_AXES', location=chassis_loc)
fixed_constraint = bpy.context.active_object
fixed_constraint.name = "Fixed_Constraint"
bpy.ops.rigidbody.constraint_add()
fixed_constraint.rigid_body_constraint.type = 'FIXED'
fixed_constraint.rigid_body_constraint.object1 = chassis
fixed_constraint.rigid_body_constraint.object2 = ground
fixed_constraint.rigid_body_constraint.breaking_threshold = fixed_constraint_breaking_threshold

# Create wheels
for i, pos in enumerate(wheel_positions):
    # Create cylinder (aligned along Z by default)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    
    # Rotate 90° around X-axis to align cylinder axis with Y-axis for X-rotation
    wheel.rotation_euler = (math.radians(90), 0, 0)
    
    # Apply rigid body physics
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.collision_shape = 'CYLINDER'
    
    # Create hinge constraint between wheel and chassis
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
    hinge = bpy.context.active_object
    hinge.name = f"Hinge_{i}"
    bpy.ops.rigidbody.constraint_add()
    hinge.rigid_body_constraint.type = 'HINGE'
    hinge.rigid_body_constraint.object1 = wheel
    hinge.rigid_body_constraint.object2 = chassis
    hinge.rigid_body_constraint.use_limit_ang_z = True
    hinge.rigid_body_constraint.limit_ang_z_lower = 0
    hinge.rigid_body_constraint.limit_ang_z_upper = 0
    hinge.rigid_body_constraint.use_motor_ang = True
    hinge.rigid_body_constraint.motor_ang_velocity = motor_velocity
    
    # Set hinge axis to X (local to constraint object)
    hinge.rigid_body_constraint.axis = 'X'

# Set simulation parameters for consistent behavior
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Rover construction complete. Motors set to", motor_velocity, "rad/s")