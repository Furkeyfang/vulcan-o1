import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
chassis_dim = (3.0, 1.0, 0.5)
chassis_loc = (0.0, 0.0, 0.25)
rudder_dim = (0.5, 1.0, 0.1)
rudder_loc = (0.0, -1.45, 0.75)
hinge_pivot = (0.0, -1.5, 0.25)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 2.0
simulation_frames = 100

# Create chassis (main robot body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Cube default size=2
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.enabled = True
chassis.rigid_body.mass = 5.0  # Reasonable mass for chassis

# Create rudder (vertical fin)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=rudder_loc)
rudder = bpy.context.active_object
rudder.name = "Rudder"
rudder.scale = (rudder_dim[0]/2, rudder_dim[1]/2, rudder_dim[2]/2)
bpy.ops.rigidbody.object_add()
rudder.rigid_body.type = 'ACTIVE'
rudder.rigid_body.enabled = True
rudder.rigid_body.mass = 0.5  # Lighter than chassis

# Create hinge constraint object
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge = bpy.context.active_object
hinge.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
hinge.rigid_body_constraint.type = 'HINGE'
hinge.rigid_body_constraint.object1 = chassis
hinge.rigid_body_constraint.object2 = rudder
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = -math.radians(45)  # ±45° limit
hinge.rigid_body_constraint.limit_ang_z_upper = math.radians(45)
hinge.rigid_body_constraint.use_motor_ang = True
hinge.rigid_body_constraint.motor_ang_target_velocity = motor_velocity
hinge.rigid_body_constraint.motor_ang_max_impulse = 2.0  # Torque limit
hinge.rigid_body_constraint.axis = hinge_axis

# Set initial velocities to zero
chassis.rigid_body.linear_velocity = (0.0, 0.0, 0.0)
chassis.rigid_body.angular_velocity = (0.0, 0.0, 0.0)
rudder.rigid_body.linear_velocity = (0.0, 0.0, 0.0)
rudder.rigid_body.angular_velocity = (0.0, 0.0, 0.0)

# Configure physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = simulation_frames

# Optional: Add ground plane for friction
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print("Hinge-driven rudder system created. Motor velocity:", motor_velocity, "rad/s")
print("Simulation will run for", simulation_frames, "frames")