import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.4)
wheel_radius = 0.4
wheel_depth = 0.15
wheel_positions = [
    (1.5, 0.75, 0.4),
    (1.5, -0.75, 0.4),
    (-1.5, 0.75, 0.4),
    (-1.5, -0.75, 0.4)
]
outrigger_dim = (0.2, 1.5, 0.1)
outrigger_left_loc = (0.0, 0.85, 0.25)
outrigger_right_loc = (0.0, -0.85, 0.25)
motor_velocity = 4.5

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'

# Create outrigger bars
outrigger_locs = [outrigger_left_loc, outrigger_right_loc]
for i, loc in enumerate(outrigger_locs):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    outrigger = bpy.context.active_object
    outrigger.name = f"Outrigger_{i+1}"
    outrigger.scale = outrigger_dim
    bpy.ops.rigidbody.object_add()
    outrigger.rigid_body.type = 'ACTIVE'
    
    # Fixed constraint to chassis
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_Outrigger_{i+1}"
    constraint.empty_display_type = 'ARROWS'
    constraint.location = loc
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = outrigger

# Create wheels
for i, pos in enumerate(wheel_positions):
    # Create cylinder (default aligned to Z)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=pos)
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"
    # Rotate 90° around Y to align cylinder axis with X (for hinge rotation)
    wheel.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    
    # Hinge constraint to chassis
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    hinge = bpy.context.active_object
    hinge.name = f"Hinge_Wheel_{i+1}"
    hinge.empty_display_type = 'SINGLE_ARROW'
    hinge.location = pos
    hinge.rigid_body_constraint.object1 = chassis
    hinge.rigid_body_constraint.object2 = wheel
    hinge.rigid_body_constraint.axis = 'X'  # Rotation axis for forward motion
    # Configure motor
    hinge.rigid_body_constraint.use_motor = True
    hinge.rigid_body_constraint.use_angular_motor = True
    hinge.rigid_body_constraint.motor_lin_velocity = 0
    hinge.rigid_body_constraint.motor_ang_velocity = motor_velocity

# Set physics scene properties for stability
bpy.context.scene.rigidbody_world.steps_per_second = 120
bpy.context.scene.rigidbody_world.solver_iterations = 50