import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
base_dim = (4.0, 4.0, 1.0)
base_loc = (0.0, 0.0, 0.5)
mast_dim = (0.5, 0.5, 8.0)
mast_loc = (0.0, 0.0, 5.0)
left_arm_dim = (3.0, 0.3, 0.3)
left_arm_loc = (-1.5, 0.0, 9.0)
left_cw_radius = 0.4
left_cw_depth = 0.5
left_cw_loc = (0.2, 0.0, 9.0)
left_load_dim = (0.5, 0.5, 0.5)
left_load_loc = (-3.0, 0.0, 9.0)
left_load_mass = 200.0
right_arm_dim = (6.0, 0.3, 0.3)
right_arm_loc = (3.0, 0.0, 9.0)
right_cw_radius = 0.6
right_cw_depth = 0.5
right_cw_loc = (-0.3, 0.0, 9.0)
right_load_dim = (0.8, 0.8, 0.8)
right_load_loc = (6.0, 0.0, 9.0)
right_load_mass = 500.0
arm_density = 7850.0
left_cw_density = 1590.0
right_cw_density = 2120.0
hinge_velocity = 0.5

# Helper to add rigid body
def add_rigidbody(obj, body_type='ACTIVE', mass=1.0):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    obj.rigid_body.mass = mass

# Create Base (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
add_rigidbody(base, 'PASSIVE', 10000.0)  # Heavy base

# Create Mast (Active, but fixed to base)
bpy.ops.mesh.primitive_cube_add(size=1, location=mast_loc)
mast = bpy.context.active_object
mast.scale = mast_dim
mast_volume = mast_dim[0] * mast_dim[1] * mast_dim[2]
add_rigidbody(mast, 'ACTIVE', arm_density * mast_volume)

# Fixed constraint between Base and Mast
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,5))
constraint_empty = bpy.context.active_object
constraint_empty.empty_display_size = 0.5
bpy.ops.rigidbody.constraint_add()
constraint = constraint_empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = base
constraint.object2 = mast

# Create Left Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=left_arm_loc)
left_arm = bpy.context.active_object
left_arm.scale = left_arm_dim
left_arm_volume = left_arm_dim[0] * left_arm_dim[1] * left_arm_dim[2]
add_rigidbody(left_arm, 'ACTIVE', arm_density * left_arm_volume)

# Left Counterweight (Cylinder, oriented along Y)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=left_cw_radius, depth=left_cw_depth, location=left_cw_loc)
left_cw = bpy.context.active_object
left_cw.rotation_euler = (math.pi/2, 0, 0)  # Rotate to align depth along Y
left_cw_volume = math.pi * left_cw_radius**2 * left_cw_depth
add_rigidbody(left_cw, 'ACTIVE', left_cw_density * left_cw_volume)

# Left Load
bpy.ops.mesh.primitive_cube_add(size=1, location=left_load_loc)
left_load = bpy.context.active_object
left_load.scale = left_load_dim
add_rigidbody(left_load, 'ACTIVE', left_load_mass)

# Fixed constraints for left arm assembly
for obj in [left_cw, left_load]:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj.location)
    fix_empty = bpy.context.active_object
    fix_empty.empty_display_size = 0.3
    bpy.ops.rigidbody.constraint_add()
    fix_con = fix_empty.rigid_body_constraint
    fix_con.type = 'FIXED'
    fix_con.object1 = left_arm
    fix_con.object2 = obj

# Create Right Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=right_arm_loc)
right_arm = bpy.context.active_object
right_arm.scale = right_arm_dim
right_arm_volume = right_arm_dim[0] * right_arm_dim[1] * right_arm_dim[2]
add_rigidbody(right_arm, 'ACTIVE', arm_density * right_arm_volume)

# Right Counterweight
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=right_cw_radius, depth=right_cw_depth, location=right_cw_loc)
right_cw = bpy.context.active_object
right_cw.rotation_euler = (math.pi/2, 0, 0)
right_cw_volume = math.pi * right_cw_radius**2 * right_cw_depth
add_rigidbody(right_cw, 'ACTIVE', right_cw_density * right_cw_volume)

# Right Load
bpy.ops.mesh.primitive_cube_add(size=1, location=right_load_loc)
right_load = bpy.context.active_object
right_load.scale = right_load_dim
add_rigidbody(right_load, 'ACTIVE', right_load_mass)

# Fixed constraints for right arm assembly
for obj in [right_cw, right_load]:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj.location)
    fix_empty = bpy.context.active_object
    fix_empty.empty_display_size = 0.3
    bpy.ops.rigidbody.constraint_add()
    fix_con = fix_empty.rigid_body_constraint
    fix_con.type = 'FIXED'
    fix_con.object1 = right_arm
    fix_con.object2 = obj

# Hinge constraints for arms (attached to mast)
hinge_loc = (0.0, 0.0, 9.0)
for arm, name in [(left_arm, "Left"), (right_arm, "Right")]:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_loc)
    hinge_empty = bpy.context.active_object
    hinge_empty.name = f"Hinge_{name}"
    hinge_empty.empty_display_size = 0.4
    bpy.ops.rigidbody.constraint_add()
    hinge = hinge_empty.rigid_body_constraint
    hinge.type = 'HINGE'
    hinge.object1 = mast
    hinge.object2 = arm
    hinge.use_limit_z = False
    hinge.use_motor_z = True
    hinge.motor_velocity_z = hinge_velocity
    hinge.motor_max_impulse_z = 1000.0

# Set up rigid body world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.frame_end = 500  # For 360° rotation test