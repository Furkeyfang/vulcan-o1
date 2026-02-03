import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Enable rigidbody physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Extract parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_loc = (0.0, 0.0, 0.4)

left_y = -0.75
right_y = 0.75

front_rad = 0.3
front_depth = 0.1
rear_rad = 0.25
rear_depth = 0.1

front_left = (-1.25, left_y, 0.4)
rear_left = (1.25, left_y, 0.4)
front_right = (-1.25, right_y, 0.4)
rear_right = (1.25, right_y, 0.4)

track_dim = (2.5, 0.6, 0.05)
track_left = (0.0, left_y, 0.4)
track_right = (0.0, right_y, 0.4)

left_vel = 2.0
right_vel = -2.0

# Helper function: create cylinder with axis along Y
def create_wheel(name, radius, depth, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° around X to align cylinder axis with Y (track width direction)
    wheel.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.rigidbody.object_add()
    return wheel

# Helper function: create box
def create_box(name, dim, location):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    box = bpy.context.active_object
    box.name = name
    box.scale = (dim[0], dim[1], dim[2])
    bpy.ops.rigidbody.object_add()
    return box

# 1. Create chassis
chassis = create_box("Chassis", chassis_dim, chassis_loc)

# 2. Create left track assembly
front_left_wheel = create_wheel("Front_Left_Wheel", front_rad, front_depth, front_left)
rear_left_wheel = create_wheel("Rear_Left_Wheel", rear_rad, rear_depth, rear_left)
track_left_plate = create_box("Left_Track_Plate", track_dim, track_left)

# 3. Create right track assembly
front_right_wheel = create_wheel("Front_Right_Wheel", front_rad, front_depth, front_right)
rear_right_wheel = create_wheel("Rear_Right_Wheel", rear_rad, rear_depth, rear_right)
track_right_plate = create_box("Right_Track_Plate", track_dim, track_right)

# 4. Add hinge constraints for wheels (parented to chassis)
def add_hinge(name, obj, pivot_loc, axis='X'):
    # Create empty for constraint pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=pivot_loc)
    empty = bpy.context.active_object
    empty.name = name + "_Pivot"
    empty.parent = chassis
    
    # Add constraint to wheel
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.constraint_add()
    const = obj.rigid_body_constraint
    const.type = 'HINGE'
    const.object1 = chassis  # parent
    const.object2 = obj     # child
    const.pivot_type = 'CUSTOM'
    const.use_breaking = False
    
    # Set pivot to empty location (in world coordinates)
    const.pivot_x = pivot_loc[0]
    const.pivot_y = pivot_loc[1]
    const.pivot_z = pivot_loc[2]
    
    # Axis direction (global coordinates)
    if axis == 'X':
        const.axis_x = 1
        const.axis_y = 0
        const.axis_z = 0
    return const

# Left hinges
left_front_hinge = add_hinge("Left_Front_Hinge", front_left_wheel, front_left, 'X')
left_rear_hinge = add_hinge("Left_Rear_Hinge", rear_left_wheel, rear_left, 'X')

# Right hinges
right_front_hinge = add_hinge("Right_Front_Hinge", front_right_wheel, front_right, 'X')
right_rear_hinge = add_hinge("Right_Rear_Hinge", rear_right_wheel, rear_right, 'X')

# 5. Add fixed constraints for track plates
def add_fixed_constraint(name, obj_a, obj_b):
    bpy.context.view_layer.objects.active = obj_a
    bpy.ops.rigidbody.constraint_add()
    const = obj_a.rigid_body_constraint
    const.name = name
    const.type = 'FIXED'
    const.object1 = obj_a
    const.object2 = obj_b
    const.use_breaking = False
    return const

# Left: plate fixed to both left wheels
add_fixed_constraint("Left_Track_Front", track_left_plate, front_left_wheel)
add_fixed_constraint("Left_Track_Rear", track_left_plate, rear_left_wheel)

# Right: plate fixed to both right wheels
add_fixed_constraint("Right_Track_Front", track_right_plate, front_right_wheel)
add_fixed_constraint("Right_Track_Rear", track_right_plate, rear_right_wheel)

# 6. Configure motors for differential steering
left_front_hinge.use_motor = True
left_front_hinge.motor_angular_target_velocity = left_vel
left_front_hinge.motor_max_impulse = 10.0  # Sufficient torque

right_front_hinge.use_motor = True
right_front_hinge.motor_angular_target_velocity = right_vel
right_front_hinge.motor_max_impulse = 10.0

# 7. Set simulation parameters
bpy.context.scene.frame_end = 150
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Tracked vehicle constructed with differential steering.")
print(f"Left motor: {left_vel} rad/s, Right motor: {right_vel} rad/s")