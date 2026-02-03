import bpy
import math

# ===== PARAMETERS =====
# Chassis
chassis_size_x = 3.0
chassis_size_y = 1.5
chassis_size_z = 0.4
chassis_loc = (0.0, 0.0, 0.4)

# Wheels
wheel_radius = 0.3
wheel_depth = 0.15
wheel_offset_x = 1.5
wheel_offset_y = 0.75
wheel_z = 0.3

# Motors
motor_velocity = 4.0

# Simulation
sim_frames = 300
fps = 30
ground_size = 20.0

# Wheel positions (front_right, front_left, rear_right, rear_left)
wheel_positions = [
    ( wheel_offset_x, -wheel_offset_y, wheel_z),
    ( wheel_offset_x,  wheel_offset_y, wheel_z),
    (-wheel_offset_x, -wheel_offset_y, wheel_z),
    (-wheel_offset_x,  wheel_offset_y, wheel_z)
]

# ===== SCENE SETUP =====
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set frames per second
bpy.context.scene.render.fps = fps
bpy.context.scene.frame_end = sim_frames

# ===== GROUND PLANE =====
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ===== CHASSIS =====
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_size_x, chassis_size_y, chassis_size_z)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.mass = 5.0  # Reasonable mass for chassis

# ===== WHEELS =====
wheel_objects = []
for i, pos in enumerate(wheel_positions):
    # Create cylinder (aligned along Z by default)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    
    # Rotate 90° around X so cylinder axis aligns with Y (for X-axis rotation)
    wheel.rotation_euler = (math.radians(90), 0, 0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = 0.5  # Lighter than chassis
    
    wheel_objects.append(wheel)

# ===== HINGE CONSTRAINTS =====
for i, wheel in enumerate(wheel_objects):
    # Create constraint object
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{i}"
    
    # Position at wheel center
    constraint.location = wheel.location
    
    # Configure constraint
    rb_const = constraint.rigid_body_constraint
    rb_const.object1 = chassis
    rb_const.object2 = wheel
    rb_const.use_limit_z = True
    rb_const.limit_z_lower = 0
    rb_const.limit_z_upper = 0  # No lateral rotation
    
    # Set as motor
    rb_const.use_motor_z = True
    rb_const.motor_velocity_z = motor_velocity
    rb_const.motor_max_impulse_z = 10.0

# ===== VERIFICATION SETUP =====
# Add empty at X=10 to mark verification point
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(10, 0, 1))
marker = bpy.context.active_object
marker.name = "Verification_Marker"

# ===== SIMULATION SETTINGS =====
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 1.0

print("Crawler robot assembly complete. Motors activated.")
print(f"Expected velocity: {motor_velocity * wheel_radius} m/s")
print(f"Verification: Robot should pass X=10 within {sim_frames} frames")