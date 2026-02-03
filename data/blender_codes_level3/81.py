import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
base_dim = (4.0, 2.0, 0.5)
base_loc = (0.0, 0.0, 0.0)
rack_dim = (3.0, 0.2, 0.1)
rack_loc = (0.0, 0.0, 0.3)
knuckle_dim = (0.5, 0.3, 0.2)
knuckle_left_loc = (-1.25, 0.0, 0.45)
knuckle_right_loc = (1.25, 0.0, 0.45)
wheel_radius = 0.3
wheel_depth = 0.15
wheel_left_loc = (-1.25, 0.0, 0.05)
wheel_right_loc = (1.25, 0.0, 0.05)
motor_angular_velocity = 0.5
simulation_frames = 100

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# 1. Base Platform (Static)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.name = "Base_Platform"

# 2. Rack Bar (Active, Hinged to Base)
bpy.ops.mesh.primitive_cube_add(size=1, location=rack_loc)
rack = bpy.context.active_object
rack.scale = rack_dim
bpy.ops.rigidbody.object_add()
rack.rigid_body.type = 'ACTIVE'
rack.name = "Rack_Bar"

# Create hinge constraint between Base and Rack
bpy.ops.object.empty_add(type='PLAIN_AXES', location=rack_loc)
hinge_empty = bpy.context.active_object
hinge_empty.name = "Rack_Hinge"
bpy.ops.rigidbody.constraint_add()
hinge_empty.rigid_body_constraint.type = 'HINGE'
hinge_empty.rigid_body_constraint.object1 = base
hinge_empty.rigid_body_constraint.object2 = rack
hinge_empty.rigid_body_constraint.use_limit_z = True
hinge_empty.rigid_body_constraint.limit_z_lower = -0.5
hinge_empty.rigid_body_constraint.limit_z_upper = 0.5
hinge_empty.rigid_body_constraint.use_motor_z = True
hinge_empty.rigid_body_constraint.motor_angular_target_velocity_z = motor_angular_velocity

# 3. Left Knuckle (Fixed to Rack)
bpy.ops.mesh.primitive_cube_add(size=1, location=knuckle_left_loc)
knuckle_left = bpy.context.active_object
knuckle_left.scale = knuckle_dim
bpy.ops.rigidbody.object_add()
knuckle_left.rigid_body.type = 'ACTIVE'
knuckle_left.name = "Knuckle_Left"

# Fixed constraint between Rack and Left Knuckle
bpy.ops.object.empty_add(type='PLAIN_AXES', location=knuckle_left_loc)
fixed_left_empty = bpy.context.active_object
fixed_left_empty.name = "Fixed_Left"
bpy.ops.rigidbody.constraint_add()
fixed_left_empty.rigid_body_constraint.type = 'FIXED'
fixed_left_empty.rigid_body_constraint.object1 = rack
fixed_left_empty.rigid_body_constraint.object2 = knuckle_left

# 4. Right Knuckle (Fixed to Rack)
bpy.ops.mesh.primitive_cube_add(size=1, location=knuckle_right_loc)
knuckle_right = bpy.context.active_object
knuckle_right.scale = knuckle_dim
bpy.ops.rigidbody.object_add()
knuckle_right.rigid_body.type = 'ACTIVE'
knuckle_right.name = "Knuckle_Right"

# Fixed constraint between Rack and Right Knuckle
bpy.ops.object.empty_add(type='PLAIN_AXES', location=knuckle_right_loc)
fixed_right_empty = bpy.context.active_object
fixed_right_empty.name = "Fixed_Right"
bpy.ops.rigidbody.constraint_add()
fixed_right_empty.rigid_body_constraint.type = 'FIXED'
fixed_right_empty.rigid_body_constraint.object1 = rack
fixed_right_empty.rigid_body_constraint.object2 = knuckle_right

# 5. Left Wheel (Hinged to Left Knuckle)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=wheel_left_loc)
wheel_left = bpy.context.active_object
wheel_left.rotation_euler = (math.radians(90), 0, 0)  # Orient cylinder axis along Y
bpy.ops.rigidbody.object_add()
wheel_left.rigid_body.type = 'ACTIVE'
wheel_left.name = "Wheel_Left"

# Hinge constraint between Left Knuckle and Left Wheel (Z-axis rotation)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel_left_loc)
hinge_wheel_left_empty = bpy.context.active_object
hinge_wheel_left_empty.name = "Hinge_Wheel_Left"
bpy.ops.rigidbody.constraint_add()
hinge_wheel_left_empty.rigid_body_constraint.type = 'HINGE'
hinge_wheel_left_empty.rigid_body_constraint.object1 = knuckle_left
hinge_wheel_left_empty.rigid_body_constraint.object2 = wheel_left

# 6. Right Wheel (Hinged to Right Knuckle)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=wheel_radius, depth=wheel_depth, location=wheel_right_loc)
wheel_right = bpy.context.active_object
wheel_right.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.rigidbody.object_add()
wheel_right.rigid_body.type = 'ACTIVE'
wheel_right.name = "Wheel_Right"

# Hinge constraint between Right Knuckle and Right Wheel (Z-axis rotation)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=wheel_right_loc)
hinge_wheel_right_empty = bpy.context.active_object
hinge_wheel_right_empty.name = "Hinge_Wheel_Right"
bpy.ops.rigidbody.constraint_add()
hinge_wheel_right_empty.rigid_body_constraint.type = 'HINGE'
hinge_wheel_right_empty.rigid_body_constraint.object1 = knuckle_right
hinge_wheel_right_empty.rigid_body_constraint.object2 = wheel_right

# Set simulation end frame
bpy.context.scene.frame_end = simulation_frames

# Optional: Set gravity to default (Z = -9.81) for realism
bpy.context.scene.rigidbody_world.gravity = (0, 0, -9.81)