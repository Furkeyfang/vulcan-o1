import bpy
import math

# 1. Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# 2. Define parameters from summary
chassis_dim = (3.0, 1.5, 0.4)
chassis_center_z = 0.2
wheel_radius = 0.3
wheel_depth = 0.15
wheel_z = 0.3
front_x = -1.2
rear_x = 1.2
wheel_y_offset = 0.75
motor_target_velocity = 3.0
start_pos = (0.0, 0.0, 0.2)

# 3. Create chassis (box)
bpy.ops.mesh.primitive_cube_add(size=1, location=start_pos)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (chassis_dim[0]/2, chassis_dim[1]/2, chassis_dim[2]/2)  # Blender cube size=2, so scale by half dimensions
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'ACTIVE'
chassis.rigid_body.collision_shape = 'BOX'

# 4. Function to create a wheel and attach it
def create_wheel(name, location, is_rear=False):
    # Create cylinder (default aligned along Z)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=wheel_radius,
        depth=wheel_depth,
        location=location
    )
    wheel = bpy.context.active_object
    wheel.name = name
    # Rotate 90° about Y so cylinder axis aligns with X (hinge axis)
    wheel.rotation_euler = (0, math.pi/2, 0)
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    wheel.rigid_body.type = 'ACTIVE'
    wheel.rigid_body.collision_shape = 'CYLINDER'
    wheel.rigid_body.collision_margin = 0.0  # Use shape margin
    
    # Create hinge constraint between chassis and wheel
    bpy.ops.object.select_all(action='DESELECT')
    chassis.select_set(True)
    wheel.select_set(True)
    bpy.context.view_layer.objects.active = chassis
    bpy.ops.rigidbody.constraint_add(type='HINGE')
    constraint = bpy.context.active_object
    constraint.name = f"{name}_Hinge"
    constraint.empty_display_type = 'ARROWS'
    # Set constraint properties
    constraint.rigid_body_constraint.type = 'HINGE'
    constraint.rigid_body_constraint.object1 = chassis
    constraint.rigid_body_constraint.object2 = wheel
    constraint.rigid_body_constraint.use_limit_ang_z = True  # Hinge uses angular Z limit in Blender
    constraint.rigid_body_constraint.limit_ang_z_lower = 0
    constraint.rigid_body_constraint.limit_ang_z_upper = 0
    # Motor settings for rear wheels
    if is_rear:
        constraint.rigid_body_constraint.use_motor_ang = True
        constraint.rigid_body_constraint.motor_ang_target_velocity = motor_target_velocity
    
    # Create fixed constraint for additional bonding
    bpy.ops.object.select_all(action='DESELECT')
    chassis.select_set(True)
    wheel.select_set(True)
    bpy.context.view_layer.objects.active = chassis
    bpy.ops.rigidbody.constraint_add(type='FIXED')
    fixed_constraint = bpy.context.active_object
    fixed_constraint.name = f"{name}_Fixed"
    fixed_constraint.empty_display_type = 'CUBE'
    fixed_constraint.rigid_body_constraint.object1 = chassis
    fixed_constraint.rigid_body_constraint.object2 = wheel
    
    return wheel

# 5. Create four wheels
wheel_fl = create_wheel("Wheel_FL", (front_x, -wheel_y_offset, wheel_z), is_rear=False)
wheel_fr = create_wheel("Wheel_FR", (front_x, wheel_y_offset, wheel_z), is_rear=False)
wheel_rl = create_wheel("Wheel_RL", (rear_x, -wheel_y_offset, wheel_z), is_rear=True)
wheel_rr = create_wheel("Wheel_RR", (rear_x, wheel_y_offset, wheel_z), is_rear=True)

# 6. Set up rigid body world
scene = bpy.context.scene
scene.rigidbody_world.enabled = True
scene.rigidbody_world.collection = bpy.data.collections.get("Collection")  # Default collection
scene.frame_end = 300  # Simulation length

print("Robot assembly complete. Rear-wheel motors activated.")