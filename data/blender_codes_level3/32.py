import bpy
import math

# ========== PARAMETERS FROM SUMMARY ==========
chassis_dim = (3.0, 1.5, 0.4)
chassis_center = (0.0, 0.0, 0.2)
wheel_radius = 0.3
wheel_depth = 0.15
wheel_positions = [
    (1.425, 0.75, 0.3),   # Front left
    (1.425, -0.75, 0.3),  # Front right
    (-1.425, 0.75, 0.3),  # Rear left
    (-1.425, -0.75, 0.3)  # Rear right
]
motor_velocity = 3.5
stop_threshold_x = 9.5
target_point = (10.0, 0.0, 0.0)
simulation_frames = 300
ground_size = 20.0

# ========== SCENE SETUP ==========
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set gravity for realistic motion
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# ========== GROUND PLANE ==========
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, -0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ========== CHASSIS ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_center)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 50.0  # Reasonable mass for rover
chassis.rigid_body.linear_damping = 0.1
chassis.rigid_body.angular_damping = 0.2

# ========== WHEELS ==========
wheel_objects = []
for i, pos in enumerate(wheel_positions):
    # Create cylinder (default axis: Z)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=pos
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    
    # Rotate 90° about Y to align cylinder axis with X (rotation axis for hinge)
    wheel.rotation_euler = (0.0, math.radians(90.0), 0.0)
    
    # Apply rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = 5.0
    wheel.rigid_body.linear_damping = 0.05
    wheel.rigid_body.angular_damping = 0.1
    
    # Store for constraint creation
    wheel_objects.append(wheel)

# ========== CONSTRAINTS ==========
# Fixed constraints to bond chassis components (redundant but safe)
for wheel in wheel_objects:
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{wheel.name}"
    constraint.empty_display_type = 'ARROWS'
    constraint.location = wheel.location
    
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel

# Hinge constraints for wheel rotation (actuated)
for wheel in wheel_objects:
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{wheel.name}"
    constraint.empty_display_type = 'CIRCLE'
    constraint.location = wheel.location
    
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_limit_ang_z = False
    
    # Configure as motor
    constraint.rigid_body_constraint.use_motor_ang = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
    constraint.rigid_body_constraint.motor_ang_max_torque = 100.0

# ========== SIMULATION CONTROL ==========
# Frame change handler to stop motors at threshold
def stop_motors_handler(scene):
    chassis_obj = bpy.data.objects.get("Chassis")
    if not chassis_obj:
        return
    
    # Check if chassis has passed stop threshold
    if chassis_obj.location.x >= stop_threshold_x:
        # Deactivate all hinge motors
        for obj in bpy.data.objects:
            if obj.name.startswith("Hinge_"):
                obj.rigid_body_constraint.use_motor_ang = False
                obj.rigid_body_constraint.motor_ang_target_velocity = 0.0

# Register handler (runs every frame during simulation)
bpy.app.handlers.frame_change_pre.append(stop_motors_handler)

# ========== SIMULATION EXECUTION ==========
# Configure simulation settings
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Bake simulation (headless compatible)
bpy.ops.ptcache.bake_all(bake=True)

# ========== VERIFICATION ==========
# Check final position
chassis_final = bpy.data.objects["Chassis"]
final_pos = chassis_final.location
distance_to_target = (final_pos - target_point).length

print(f"Rover final position: {final_pos}")
print(f"Distance to target (10,0,0): {distance_to_target:.3f}m")
print(f"Stopping requirement met: {distance_to_target <= 0.5}")

# Clean up handler
bpy.app.handlers.frame_change_pre.remove(stop_motors_handler)