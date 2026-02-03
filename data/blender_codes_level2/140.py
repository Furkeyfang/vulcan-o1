import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_dim = (1.0, 1.0, 10.0)
col_loc = (0.0, 0.0, 5.0)
rb_rad = 0.05
rb_ht = 10.0
rb_offsets = [(0.3, 0.3, 5.0), (0.3, -0.3, 5.0), (-0.3, 0.3, 5.0), (-0.3, -0.3, 5.0)]
pl_dim = (1.5, 1.5, 0.2)
pl_loc = (0.0, 0.0, 10.1)
load_force = -49050.0  # Newtons

# Create Concrete Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Concrete_Column"
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create Steel Rebars
rebar_names = []
for i, offset in enumerate(rb_offsets):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=rb_rad,
        depth=rb_ht,
        location=offset
    )
    rebar = bpy.context.active_object
    rebar.name = f"Rebar_{i:02d}"
    rebar.rigidbody = rebar.rigid_body
    bpy.ops.rigidbody.object_add()
    rebar.rigid_body.type = 'PASSIVE'
    rebar.rigid_body.collision_shape = 'MESH'  # Cylinder collision
    rebar_names.append(rebar.name)

# Create Fixed Constraints between Column and Rebars
for rebar_name in rebar_names:
    rebar = bpy.data.objects[rebar_name]
    
    # Create empty for constraint target
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=col_loc)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{rebar.name}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = column
    constraint.object2 = rebar
    
    # Parent constraint empty to column (organizational)
    constraint_empty.parent = column

# Create Load Plate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=pl_loc)
plate = bpy.context.active_object
plate.name = "Load_Plate"
plate.scale = pl_dim
bpy.ops.rigidbody.object_add()
plate.rigid_body.type = 'ACTIVE'
plate.rigid_body.mass = 100.0  # Arbitrary mass for stability
plate.rigid_body.collision_shape = 'BOX'
plate.rigid_body.use_margin = True
plate.rigid_body.collision_margin = 0.0

# Create Motor Constraint for Load Application
bpy.ops.object.empty_add(type='ARROWS', location=pl_loc)
motor_empty = bpy.context.active_object
motor_empty.name = "Motor_Target"
bpy.ops.rigidbody.object_add()
motor_empty.rigid_body.type = 'PASSIVE'

# Add motor constraint to plate
plate.rigid_body_constraint = plate.constraints.new(type='RIGID_BODY_JOINT')
motor_constraint = plate.rigid_body_constraint
motor_constraint.type = 'MOTOR'
motor_constraint.object1 = plate
motor_constraint.object2 = motor_empty
motor_constraint.use_linear_motor = True
motor_constraint.use_angular_motor = False
motor_constraint.lin_vel_x = 0.0
motor_constraint.lin_vel_y = 0.0
motor_constraint.lin_vel_z = 0.0  # Target velocity (static load)
motor_constraint.lin_max_impulse = abs(load_force)  # Maximum force magnitude
motor_constraint.lin_servo_target_x = pl_loc[0]
motor_constraint.lin_servo_target_y = pl_loc[1]
motor_constraint.lin_servo_target_z = pl_loc[2]
motor_constraint.use_servo_linear = True

# Configure physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.gravity[2] = 0.0  # Disable gravity for pure motor force

# Set collision margins for all rigid bodies
for obj in bpy.data.objects:
    if obj.rigid_body:
        obj.rigid_body.use_margin = True
        obj.rigid_body.collision_margin = 0.001

print("Reinforced concrete column assembly complete.")
print(f"Load force: {load_force} N applied via motor constraint.")