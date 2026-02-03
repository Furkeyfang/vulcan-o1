import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
support_dim = (0.3, 0.3, 2.0)
left_support_loc = (-1.0, 0.0, 1.5)
right_support_loc = (1.0, 0.0, 1.5)
boom_dim = (0.2, 0.2, 4.0)
left_boom_loc = (-3.0, 0.0, 2.5)
right_boom_loc = (3.0, 0.0, 2.5)
counter_dim = (0.5, 0.5, 0.5)
left_counter_loc = (-5.0, 0.0, 2.5)
right_counter_loc = (5.0, 0.0, 2.5)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 2.0
frames_to_align = 100

# Enable physics
bpy.context.scene.use_gravity = True
bpy.context.scene.gravity = (0.0, 0.0, -9.81)

# Helper: Create cube with physics
def create_cube(name, location, scale, rigid_type='ACTIVE'):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = rigid_type
    obj.rigid_body.collision_shape = 'BOX'
    return obj

# Helper: Create constraint between two objects
def create_constraint(name, obj_a, obj_b, const_type, location, use_motor=False, motor_vel=0.0):
    # Create empty for constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.active_object
    empty.name = name
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = const_type
    
    # Link objects
    constraint.object1 = obj_a
    constraint.object2 = obj_b
    
    # Configure hinge
    if const_type == 'HINGE':
        constraint.use_limit_ang_z = False
        constraint.axis = hinge_axis
        if use_motor:
            constraint.use_motor_ang = True
            constraint.motor_ang_target_velocity = motor_vel
            constraint.motor_ang_max_impulse = 10.0
    
    return constraint

# 1. Create Base Platform
base = create_cube("Base", base_loc, base_dim, 'PASSIVE')

# 2. Create Left Arm Assembly
left_support = create_cube("Left_Support", left_support_loc, support_dim, 'PASSIVE')
left_boom = create_cube("Left_Boom", left_boom_loc, boom_dim, 'ACTIVE')
left_counter = create_cube("Left_Counterweight", left_counter_loc, counter_dim, 'ACTIVE')

# 3. Create Right Arm Assembly
right_support = create_cube("Right_Support", right_support_loc, support_dim, 'PASSIVE')
right_boom = create_cube("Right_Boom", right_boom_loc, boom_dim, 'ACTIVE')
right_counter = create_cube("Right_Counterweight", right_counter_loc, counter_dim, 'ACTIVE')

# 4. Create Fixed Constraints (Support→Base)
create_constraint("Fix_LeftSupport", left_support, base, 'FIXED', left_support_loc)
create_constraint("Fix_RightSupport", right_support, base, 'FIXED', right_support_loc)

# 5. Create Hinge Constraints (Boom→Support) with Motors
# Attachment points at top of supports
left_hinge_pos = (-1.0, 0.0, 2.5)
right_hinge_pos = (1.0, 0.0, 2.5)

create_constraint("Hinge_Left", left_boom, left_support, 'HINGE', 
                  left_hinge_pos, use_motor=True, motor_vel=motor_velocity)
create_constraint("Hinge_Right", right_boom, right_support, 'HINGE', 
                  right_hinge_pos, use_motor=True, motor_vel=-motor_velocity)

# 6. Create Fixed Constraints (Counterweight→Boom)
create_constraint("Fix_LeftCounter", left_counter, left_boom, 'FIXED', left_counter_loc)
create_constraint("Fix_RightCounter", right_counter, right_boom, 'FIXED', right_counter_loc)

# 7. Set animation properties for verification
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = frames_to_align
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10

print("Dual-arm crane constructed with motorized hinges.")
print(f"Motors set to {motor_velocity} rad/s. Arms should align with Y-axis within {frames_to_align} frames.")