import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters from summary
base_dim = (3.0, 2.0, 0.5)
base_loc = (0.0, 0.0, 0.25)

arm_dim = (0.2, 2.0, 0.2)  # Will be rotated to make height=2
arm_loc = (0.0, 0.0, 1.25)
arm_rotation_x = 90.0  # Degrees

proj_dim = (0.3, 0.3, 0.3)
proj_loc = (0.0, 0.0, 2.4)

hinge_pivot = (0.0, 0.0, 0.25)
hinge_axis_y = (0.0, 1.0, 0.0)

motor_velocity = 8.0
release_frame = 6
simulation_frames = 100

arm_mass = 2.0
projectile_mass = 0.5

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Catapult Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
arm.rotation_euler = (math.radians(arm_rotation_x), 0, 0)  # Rotate to vertical
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = arm_mass

# Create Projectile
bpy.ops.mesh.primitive_cube_add(size=1, location=proj_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = proj_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'BOX'
projectile.rigid_body.mass = projectile_mass

# Add Hinge Constraint between Base and Arm
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Hinge_Pivot"

# Create constraint on Arm
arm.constraints.new(type='HINGE')
hinge_constraint = arm.constraints['Hinge']
hinge_constraint.target = base
hinge_constraint.use_limit_z = False  # Free rotation
hinge_constraint.object = arm
hinge_constraint.pivot_type = 'CENTER'

# Convert to rigid body constraint
bpy.ops.rigidbody.constraint_add()
rb_constraint = arm.rigid_body_constraint
rb_constraint.type = 'HINGE'
rb_constraint.pivot_x = hinge_pivot[0]
rb_constraint.pivot_y = hinge_pivot[1]
rb_constraint.pivot_z = hinge_pivot[2]
rb_constraint.axis_x = hinge_axis_y[0]
rb_constraint.axis_y = hinge_axis_y[1]
rb_constraint.axis_z = hinge_axis_y[2]
rb_constraint.use_motor = True
rb_constraint.motor_velocity = motor_velocity

# Add Fixed Constraint between Arm and Projectile
bpy.ops.rigidbody.constraint_add()
fixed_constraint = projectile.rigid_body_constraint
fixed_constraint.type = 'FIXED'
fixed_constraint.object1 = arm
fixed_constraint.object2 = projectile

# Keyframe motor deactivation and constraint removal
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = simulation_frames

# Motor active until release frame
rb_constraint.use_motor = True
rb_constraint.keyframe_insert(data_path="use_motor", frame=1)
rb_constraint.keyframe_insert(data_path="use_motor", frame=release_frame-1)
rb_constraint.use_motor = False
rb_constraint.keyframe_insert(data_path="use_motor", frame=release_frame)

# Fixed constraint active until release frame
fixed_constraint.keyframe_insert(data_path="enabled", frame=1)
fixed_constraint.keyframe_insert(data_path="enabled", frame=release_frame-1)
fixed_constraint.enabled = False
fixed_constraint.keyframe_insert(data_path="enabled", frame=release_frame)

# Set up rigid body world
scene.rigidbody_world.enabled = True
scene.rigidbody_world.collection = bpy.data.collections.new("RigidBodyWorld")
scene.rigidbody_world.collection.objects.link(base)
scene.rigidbody_world.collection.objects.link(arm)
scene.rigidbody_world.collection.objects.link(projectile)
scene.rigidbody_world.steps_per_second = 60
scene.rigidbody_world.solver_iterations = 10

# Ensure proper collision margins
for obj in [base, arm, projectile]:
    obj.rigid_body.collision_margin = 0.04

print("Catapult assembly complete. Motor releases at frame", release_frame)