import bpy
import math
from mathutils import Vector, Matrix

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
chassis_dim = (2.0, 1.0, 0.3)
chassis_loc = (0.0, 0.0, 0.15)
column_radius = 0.05
column_height = 0.4
column_loc = (0.0, 0.0, 0.5)
arm_dim = (0.6, 0.1, 0.05)
arm_loc = (0.0, 0.0, 0.725)
hub_dim = (0.1, 0.1, 0.1)
hub_z = 0.2
hub_left_loc = (0.8, 0.45, 0.2)
hub_right_loc = (0.8, -0.45, 0.2)
tie_radius = 0.02
tie_length = 0.3
motor_ang_vel = 2.0
frames_to_check = 100

# Create Chassis (Fixed base)
bpy.ops.mesh.primitive_cube_add(size=1, location=chassis_loc)
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = chassis_dim
bpy.ops.rigidbody.object_add()
chassis.rigid_body.type = 'PASSIVE'

# Create Steering Column (Active with hinge)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=column_radius,
    depth=column_height,
    location=column_loc
)
column = bpy.context.active_object
column.name = "Steering_Column"
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'

# Create Steering Arm (Fixed to column)
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Steering_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'

# Create Wheel Hubs (Passive, fixed position)
for loc, name in [(hub_left_loc, "Hub_Left"), (hub_right_loc, "Hub_Right")]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    hub = bpy.context.active_object
    hub.name = name
    hub.scale = hub_dim
    bpy.ops.rigidbody.object_add()
    hub.rigid_body.type = 'PASSIVE'

# Create Tie Rods (Active, diagonal placement)
def create_tie_rod(start_loc, end_loc, name):
    midpoint = ((start_loc[0] + end_loc[0]) / 2,
                (start_loc[1] + end_loc[1]) / 2,
                (start_loc[2] + end_loc[2]) / 2)
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=tie_radius,
        depth=tie_length,
        location=midpoint
    )
    rod = bpy.context.active_object
    rod.name = name
    
    # Orient cylinder along start->end vector
    direction = Vector(end_loc) - Vector(start_loc)
    rot_quat = Vector((0, 0, 1)).rotation_difference(direction)
    rod.rotation_euler = rot_quat.to_euler()
    
    bpy.ops.rigidbody.object_add()
    rod.rigid_body.type = 'ACTIVE'
    return rod

# Left tie rod (from arm end to left hub)
arm_end_left = (0, arm_dim[1]/2, arm_loc[2])
tie_left = create_tie_rod(arm_end_left, hub_left_loc, "Tie_Rod_Left")

# Right tie rod (from arm end to right hub)
arm_end_right = (0, -arm_dim[1]/2, arm_loc[2])
tie_right = create_tie_rod(arm_end_right, hub_right_loc, "Tie_Rod_Right")

# Set collision shapes for better physics
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.collision_shape = 'CONVEX_HULL'

# Create Constraints
def add_constraint(obj_a, obj_b, const_type, pivot_loc, use_motor=False):
    const = bpy.context.scene.rigidbody_world.constraints.new()
    const.type = const_type
    const.object1 = obj_a
    const.object2 = obj_b
    const.pivot_type = 'CENTER'
    
    # Set constraint location in world space
    const.disable_collisions = True
    
    if const_type == 'HINGE':
        const.use_limit_z = True
        const.limit_z_lower = -math.radians(45)
        const.limit_z_upper = math.radians(45)
        const.use_angular_motor_z = use_motor
        if use_motor:
            const.angular_motor_z_target_velocity = motor_ang_vel
            const.angular_motor_z_max_impulse = 5.0

# 1. Chassis-Column Hinge (Motorized)
add_constraint(chassis, column, 'HINGE', column_loc, use_motor=True)

# 2. Column-Arm Fixed
add_constraint(column, arm, 'FIXED', arm_loc, use_motor=False)

# 3. Arm-TieRod Hinges (at arm ends)
arm_end_left_world = arm.matrix_world @ Vector(arm_end_left)
arm_end_right_world = arm.matrix_world @ Vector(arm_end_right)
add_constraint(arm, tie_left, 'HINGE', arm_end_left_world, use_motor=False)
add_constraint(arm, tie_right, 'HINGE', arm_end_right_world, use_motor=False)

# 4. TieRod-Hub Hinges
add_constraint(tie_left, bpy.data.objects["Hub_Left"], 'HINGE', hub_left_loc, use_motor=False)
add_constraint(tie_right, bpy.data.objects["Hub_Right"], 'HINGE', hub_right_loc, use_motor=False)

# Set simulation parameters
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10
bpy.context.scene.frame_end = frames_to_check