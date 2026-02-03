import bpy
import math

# 1. Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define variables from parameter_summary
chassis_dim = (3.0, 1.0, 0.3)
chassis_loc = (0.0, 0.0, 0.45)
wheel_radius = 0.4
wheel_depth = 0.2
front_wheel_loc = (0.0, 1.6, 0.4)
rear_wheel_loc = (0.0, -1.6, 0.4)
hinge_motor_velocity = 7.5
chassis_mass = 10.0
wheel_mass = 2.0
ground_size = 20.0
sim_frames = 200

# 3. Create ground plane (passive rigid body)
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# 4. Create chassis (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.mass = chassis_mass

# 5. Function to create wheel with hinge constraint
def create_wheel(name, location):
    # Create cylinder (aligned along Z by default)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° about X so cylinder axis aligns with Y (rotation in radians)
    wheel.rotation_euler = (math.radians(90), 0, 0)
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.mass = wheel_mass
    
    # Create empty for hinge constraint at wheel location
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    hinge = bpy.context.active_object
    hinge.name = name + "_hinge"
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    hinge.rigid_body_constraint.type = 'HINGE'
    # Set constraint objects: object1=chassis, object2=wheel
    hinge.rigid_body_constraint.object1 = chassis
    hinge.rigid_body_constraint.object2 = wheel
    # Axis: Y for rotation around global Y
    hinge.rigid_body_constraint.use_limit_ang_z = True
    hinge.rigid_body_constraint.limit_ang_z_lower = 0
    hinge.rigid_body_constraint.limit_ang_z_upper = 0
    # Enable motor
    hinge.rigid_body_constraint.use_motor_ang = True
    hinge.rigid_body_constraint.motor_ang_velocity = hinge_motor_velocity
    return wheel

# 6. Create both wheels
front_wheel = create_wheel("front_wheel", front_wheel_loc)
rear_wheel = create_wheel("rear_wheel", rear_wheel_loc)

# 7. Setup simulation parameters
scene = bpy.context.scene
scene.frame_end = sim_frames
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 50

# 8. Verification setup: print starting and final positions
print(f"Vehicle start position: {chassis.location}")
print(f"Simulation will run for {sim_frames} frames")

# Note: Actual simulation baking requires bpy.ops.ptcache.bake_all()
# but in headless mode we might step through frames.
# For completeness, we add operators to bake simulation.
bpy.ops.ptcache.free_all()
bpy.ops.ptcache.bake_all(bake=True)