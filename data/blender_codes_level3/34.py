import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ========== PARAMETERS ==========
chassis_length = 2.0
chassis_width = 1.5
chassis_height = 0.3
chassis_loc = (0.0, 0.0, 0.15)
chassis_mass = 10.0

wheel_radius = 0.3
wheel_depth = 0.15
wheel_mass = 2.0

wheel_offsets = [
    (-1.0, 0.75, 0.3),   # Front Left
    (1.0, 0.75, 0.3),    # Front Right
    (-1.0, -0.75, 0.3),  # Rear Left
    (1.0, -0.75, 0.3)    # Rear Right
]

motor_target_velocity = 6.0
motor_max_impulse = 10.0

frame_end = 200
gravity_z = -9.81

# ========== SCENE SETUP ==========
scene = bpy.context.scene
scene.frame_end = frame_end
scene.gravity = (0, 0, gravity_z)

# Enable rigid body world
if not scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

# ========== GROUND PLANE ==========
bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# ========== CHASSIS ==========
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_length, chassis_width, chassis_height)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass

# ========== WHEELS ==========
wheel_objects = []
for i, offset in enumerate(wheel_offsets):
    # Create cylinder (default axis: Z)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=offset
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    
    # Rotate 90° around Y to align rotation axis with X
    wheel.rotation_euler = (0, math.pi/2, 0)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    wheel_objects.append(wheel)
    
    # ========== HINGE CONSTRAINT ==========
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=offset)
    pivot = bpy.context.active_object
    pivot.name = f"HingePivot_{i}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{i}"
    constraint.rigid_body_constraint.type = 'HINGE'
    
    # Link constraint to pivot empty
    constraint.location = offset
    
    # Set constraint objects
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    
    # Set pivot in local coordinates
    # For chassis: offset from chassis center to wheel position
    chassis_pivot = (
        offset[0] - chassis_loc[0],
        offset[1] - chassis_loc[1],
        offset[2] - chassis_loc[2]
    )
    constraint.rigid_body_constraint.pivot_type = 'PIVOT'
    constraint.rigid_body_constraint.use_breaking = False
    
    # Configure motor
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_target_velocity
    constraint.rigid_body_constraint.motor_max_impulse = motor_max_impulse
    constraint.rigid_body_constraint.motor_ang_servo_target_velocity = motor_target_velocity
    
    # Parent constraint to pivot for organization (optional)
    constraint.parent = pivot

# ========== FINAL SETUP ==========
# Set collision margins (optional but recommended)
for obj in [chassis] + wheel_objects:
    obj.rigid_body.collision_margin = 0.04

# Ensure all objects are visible in viewport
for obj in bpy.context.scene.objects:
    obj.hide_viewport = False
    obj.hide_render = False

print("Mini rover construction complete. All four wheels are motorized.")
print(f"Target velocity: {motor_target_velocity} rad/s")
print(f"Simulation length: {frame_end} frames")