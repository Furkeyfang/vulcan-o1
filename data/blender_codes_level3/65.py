import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
crane_radius = 0.2
crane_height = 4.0
crane_loc = (0.0, 0.0, 2.5)
boom_dim = (4.0, 0.3, 0.3)
boom_loc = (2.0, 0.0, 4.5)
catapult_dim = (2.0, 0.2, 0.2)
catapult_loc = (5.0, 0.0, 4.5)
projectile_dim = (0.2, 0.2, 0.2)
projectile_loc = (6.0, 0.0, 4.7)
boom_hinge_pivot = (0.0, 0.0, 4.5)
catapult_hinge_pivot = (4.0, 0.0, 4.5)
boom_motor_velocity = 2.0
catapult_motor_velocity = 50.0
base_mass = 100.0
crane_mass = 10.0
boom_mass = 2.0
catapult_mass = 1.0
projectile_mass = 0.5

# Enable rigid body world
bpy.context.scene.rigidbody_world.enabled = True

# 1. Create Base (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.mass = base_mass

# 2. Create Crane Column (Active but constrained)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=crane_radius,
    depth=crane_height,
    location=crane_loc
)
crane = bpy.context.active_object
crane.name = "Crane"
bpy.ops.rigidbody.object_add()
crane.rigid_body.type = 'ACTIVE'
crane.rigid_body.mass = crane_mass

# 3. Create Boom (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=boom_loc)
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.mass = boom_mass

# 4. Create Catapult Arm (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=catapult_loc)
catapult = bpy.context.active_object
catapult.name = "Catapult"
catapult.scale = catapult_dim
bpy.ops.rigidbody.object_add()
catapult.rigid_body.type = 'ACTIVE'
catapult.rigid_body.mass = catapult_mass

# 5. Create Projectile (Active)
bpy.ops.mesh.primitive_cube_add(size=1, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
projectile.scale = projectile_dim
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.mass = projectile_mass

# 6. Create Constraints
# Base-Crane Fixed Constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
fixed_empty = bpy.context.active_object
fixed_empty.name = "Fixed_Constraint"
fixed_empty.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
fixed_empty.rigid_body_constraint.type = 'FIXED'
fixed_empty.rigid_body_constraint.object1 = base
fixed_empty.rigid_body_constraint.object2 = crane

# Crane-Boom Hinge Constraint (Z-axis)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=boom_hinge_pivot)
boom_hinge = bpy.context.active_object
boom_hinge.name = "Boom_Hinge"
boom_hinge.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
boom_hinge.rigid_body_constraint.type = 'HINGE'
boom_hinge.rigid_body_constraint.object1 = crane
boom_hinge.rigid_body_constraint.object2 = boom
boom_hinge.rigid_body_constraint.use_limit_z = True
boom_hinge.rigid_body_constraint.limit_z_upper = 3.14159  # 180 degrees
boom_hinge.rigid_body_constraint.limit_z_lower = -3.14159
boom_hinge.rigid_body_constraint.use_motor_z = True
boom_hinge.rigid_body_constraint.motor_target_velocity_z = boom_motor_velocity
boom_hinge.rigid_body_constraint.motor_max_impulse_z = 10.0

# Boom-Catapult Hinge Constraint (Y-axis)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=catapult_hinge_pivot)
catapult_hinge = bpy.context.active_object
catapult_hinge.name = "Catapult_Hinge"
catapult_hinge.empty_display_size = 0.3
bpy.ops.rigidbody.constraint_add()
catapult_hinge.rigid_body_constraint.type = 'HINGE'
catapult_hinge.rigid_body_constraint.object1 = boom
catapult_hinge.rigid_body_constraint.object2 = catapult
catapult_hinge.rigid_body_constraint.use_limit_y = True
catapult_hinge.rigid_body_constraint.limit_y_upper = 1.5708  # 90 degrees up
catapult_hinge.rigid_body_constraint.limit_y_lower = 0.0     # Start horizontal
catapult_hinge.rigid_body_constraint.use_motor_y = True
catapult_hinge.rigid_body_constraint.motor_target_velocity_y = 0.0  # Initially off
catapult_hinge.rigid_body_constraint.motor_max_impulse_y = 100.0

# 7. Set up animation sequence
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300

# Boom motor on from frame 1-100
boom_hinge.rigid_body_constraint.motor_target_velocity_z = boom_motor_velocity
boom_hinge.rigid_body_constraint.keyframe_insert(data_path="motor_target_velocity_z", frame=1)
boom_hinge.rigid_body_constraint.motor_target_velocity_z = 0.0
boom_hinge.rigid_body_constraint.keyframe_insert(data_path="motor_target_velocity_z", frame=100)

# Catapult motor impulse at frame 120
catapult_hinge.rigid_body_constraint.motor_target_velocity_y = 0.0
catapult_hinge.rigid_body_constraint.keyframe_insert(data_path="motor_target_velocity_y", frame=1)
catapult_hinge.rigid_body_constraint.motor_target_velocity_y = catapult_motor_velocity
catapult_hinge.rigid_body_constraint.keyframe_insert(data_path="motor_target_velocity_y", frame=120)
catapult_hinge.rigid_body_constraint.motor_target_velocity_y = 0.0
catapult_hinge.rigid_body_constraint.keyframe_insert(data_path="motor_target_velocity_y", frame=121)

# Set gravity
bpy.context.scene.gravity = (0, 0, -9.81)

print("Crane-mounted catapult mechanism created successfully.")
print("Simulation sequence: Boom rotates (frames 1-100), Catapult launches at frame 120.")