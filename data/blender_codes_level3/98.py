import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract parameters
base_dim = (5.0, 5.0, 0.8)
base_loc = (0.0, 0.0, 0.0)
turntable_radius = 2.0
turntable_height = 0.5
turntable_loc = (0.0, 0.0, 0.65)
hinge_loc = (0.0, 0.0, 0.4)
motor_velocity = 1.0
simulation_frames = 100

# Enable rigid body physics (headless-safe)
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create base platform (cube)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "Base_Platform"

# Make base passive rigid body
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Add fixed constraint to ground
bpy.ops.object.constraint_add(type='FIXED')
base.constraints["Fixed"].name = "Ground_Anchor"

# Create turntable (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=turntable_radius,
    depth=turntable_height,
    location=turntable_loc
)
turntable = bpy.context.active_object
turntable.name = "Turntable"

# Make turntable active rigid body
bpy.ops.rigidbody.object_add()
turntable.rigid_body.type = 'ACTIVE'
turntable.rigid_body.collision_shape = 'CYLINDER'

# Create hinge constraint empty
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_loc)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Constraint"
hinge_empty.empty_display_size = 1.0

# Add rigid body constraint component
bpy.ops.rigidbody.constraint_add()
constraint = hinge_empty.rigid_body_constraint
constraint.type = 'HINGE'
constraint.use_limit_ang_z = False  # Free rotation
constraint.object1 = base
constraint.object2 = turntable

# Configure motor
constraint.use_motor_ang_z = True
constraint.motor_ang_z_velocity = motor_velocity
constraint.motor_ang_z_max_impulse = 100.0  # Sufficient torque

# Set simulation duration
bpy.context.scene.frame_end = simulation_frames

# Optional: Set gravity to Earth standard
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -9.81)

print(f"Crane steering mechanism built. Base: {base.name}, Turntable: {turntable.name}")
print(f"Hinge motor set to {motor_velocity} rad/s. Simulation: {simulation_frames} frames.")