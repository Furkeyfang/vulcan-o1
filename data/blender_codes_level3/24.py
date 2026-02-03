import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.4)
payload_dim = (2.0, 1.0, 0.2)
payload_loc = (0.0, 0.0, 0.8)
wheel_radius = 0.3
wheel_depth = 0.15
wheel_positions = [(1.5, 0.75, 0.2), (1.5, -0.75, 0.2), (-1.5, 0.75, 0.2), (-1.5, -0.75, 0.2)]
hinge_axis = (1.0, 0.0, 0.0)
motor_velocity = 15.0
simulation_frames = 200
ground_size = (20.0, 20.0, 0.2)
ground_loc = (0.0, 0.0, -0.1)

# Create ground plane
bpy.ops.mesh.primitive_cube_add(size=1.0, location=ground_loc)
ground = bpy.context.active_object
ground.scale = ground_size
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.name = "Ground"

# Create chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = 20.0  # Heavier than wheels
chassis.name = "Chassis"

# Create payload platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=payload_loc)
payload = bpy.context.active_object
payload.scale = payload_dim
bpy.ops.rigidbody.object_add()
payload.rigid_body.mass = 5.0
payload.name = "Payload"

# Fix payload to chassis with Fixed constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=chassis_loc)
constraint_empty = bpy.context.active_object
constraint_empty.name = "Fix_Constraint"
constraint_empty.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = chassis
constraint.object2 = payload

# Create wheels
wheel_objects = []
for i, pos in enumerate(wheel_positions):
    # Cylinder default orientation is Z-up, rotate 90° around X to align axis with X
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, 
                                        location=pos, rotation=(math.radians(90.0), 0.0, 0.0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = 2.0  # Lighter than chassis
    wheel.rigid_body.linear_damping = 0.1
    wheel.rigid_body.angular_damping = 0.1
    wheel_objects.append(wheel)
    
    # Create hinge constraint between chassis and wheel
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pos)
    hinge_empty = bpy.context.active_object
    hinge_empty.name = f"Hinge_{i}"
    hinge_empty.empty_display_size = 0.3
    bpy.ops.rigidbody.constraint_add()
    hinge = hinge_empty.rigid_body_constraint
    hinge.type = 'HINGE'
    hinge.object1 = chassis
    hinge.object2 = wheel
    hinge.axis = hinge_axis
    hinge.use_limit = False
    hinge.use_motor = True
    hinge.motor_velocity = motor_velocity
    hinge.motor_max_impulse = 10.0

# Configure simulation settings
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = simulation_frames

# Optional: Run simulation in background (uncomment to auto-run)
# for frame in range(1, simulation_frames + 1):
#     bpy.context.scene.frame_set(frame)
#     bpy.ops.rigidbody.world_sync()
# final_pos = chassis.matrix_world.translation
# print(f"Chassis final position: {final_pos}")
# print(f"Distance traveled: {final_pos.x}")

# Set viewport display (optional, for visualization if not headless)
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.show_wire = True
        obj.show_all_edges = True