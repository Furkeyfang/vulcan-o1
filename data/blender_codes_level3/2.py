import bpy
import math

# ========== 1. Clear Scene ==========
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# ========== 2. Define Variables from Summary ==========
chassis_length_x = 4.0
chassis_width_y = 2.0
chassis_height_z = 0.5
chassis_center_z = 1.25
wheel_radius = 0.5
wheel_depth = 0.2
wheel_center_z = 0.5
corner_positions = [(2,1), (2,-1), (-2,1), (-2,-1)]
motor_angular_velocity = 7.2
ground_size = 40.0
ground_location_z = 0.0
simulation_fps = 60
simulation_substeps = 10
chassis_mass = 50.0
wheel_mass = 5.0
wheel_friction = 1.0
ground_friction = 1.0

# ========== 3. Setup Physics World ==========
bpy.context.scene.rigidbody_world.steps_per_second = simulation_fps
bpy.context.scene.rigidbody_world.solver_iterations = simulation_substeps

# ========== 4. Create Ground Plane ==========
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,ground_location_z))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.friction = ground_friction

# ========== 5. Create Chassis Platform ==========
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,chassis_center_z))
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_length_x, chassis_width_y, chassis_height_z)
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'  # Chassis carried by wheels
chassis.rigid_body.mass = chassis_mass
chassis.rigid_body.linear_damping = 0.0
chassis.rigid_body.angular_damping = 0.0

# ========== 6. Create Wheels and Hinge Constraints ==========
wheel_objects = []
for i, (cx, cy) in enumerate(corner_positions):
    # Create cylinder (axis along Z initially)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=(cx, cy, wheel_center_z))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    # Rotate 90° around Y so cylinder axis aligns with global X (hinge axis)
    wheel.rotation_euler = (0, math.pi/2, 0)
    # Apply rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.mass = wheel_mass
    wheel.rigid_body.friction = wheel_friction
    wheel.rigid_body.linear_damping = 0.0
    wheel.rigid_body.angular_damping = 0.0
    wheel_objects.append(wheel)
    
    # Create Hinge Constraint between Chassis and Wheel
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Hinge_{i}"
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    # Pivot at wheel center (already in world coordinates)
    constraint.location = (cx, cy, wheel_center_z)
    # Axis is global X (1,0,0)
    constraint.rigid_body_constraint.axis = 'X'
    # Enable motor
    constraint.rigid_body_constraint.use_motor = True
    constraint.rigid_body_constraint.motor_type = 'VELOCITY'
    constraint.rigid_body_constraint.motor_lin_target_velocity = 0.0
    constraint.rigid_body_constraint.motor_ang_target_velocity = motor_angular_velocity

# ========== 7. Set Frame Range and Verify ==========
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250
bpy.context.scene.frame_current = 1

print("Rover constructed with motorized wheels.")
print(f"Target displacement: {motor_angular_velocity * wheel_radius * (bpy.context.scene.frame_end / simulation_fps):.2f} meters")