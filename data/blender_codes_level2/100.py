import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters from summary
ground_size = 10.0
column_dim = (0.5, 0.5, 9.0)
column_loc = (0.0, 0.0, 4.5)
arm_dim = (1.5, 0.2, 0.2)
arm_loc = (0.75, 0.0, 8.9)
cube_dim = (0.3, 0.3, 0.3)
cube_loc = (1.5, 0.0, 8.9)
load_mass = 70.0
steel_density = 7850.0
hinge_loc = (0.0, 0.0, 9.0)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create vertical column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'ACTIVE'
column.rigid_body.collision_shape = 'BOX'
column.rigid_body.mass = column_dim[0] * column_dim[1] * column_dim[2] * steel_density

# Create horizontal arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.rigid_body.collision_shape = 'BOX'
arm.rigid_body.mass = arm_dim[0] * arm_dim[1] * arm_dim[2] * steel_density

# Create antenna load cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=cube_loc)
cube = bpy.context.active_object
cube.name = "AntennaLoad"
cube.scale = cube_dim
bpy.ops.rigidbody.object_add()
cube.rigid_body.type = 'ACTIVE'
cube.rigid_body.collision_shape = 'BOX'
cube.rigid_body.mass = load_mass

# Set up physics world
bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
bpy.context.scene.rigidbody_world.point_cache.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

# Create constraints
# 1. Fixed constraint between ground and column base
bpy.ops.rigidbody.constraint_add()
constraint1 = bpy.context.active_object
constraint1.name = "Base_Fixed"
constraint1.empty_display_type = 'ARROWS'
constraint1.location = (0, 0, 0)
constraint1.rigid_body_constraint.type = 'FIXED'
constraint1.rigid_body_constraint.object1 = ground
constraint1.rigid_body_constraint.object2 = column

# 2. Hinge constraint between column top and arm
bpy.ops.rigidbody.constraint_add()
constraint2 = bpy.context.active_object
constraint2.name = "Column_Arm_Hinge"
constraint2.empty_display_type = 'ARROWS'
constraint2.location = hinge_loc
constraint2.rigid_body_constraint.type = 'HINGE'
constraint2.rigid_body_constraint.object1 = column
constraint2.rigid_body_constraint.object2 = arm
constraint2.rigid_body_constraint.use_limit_ang_z = True
constraint2.rigid_body_constraint.limit_ang_z_lower = -0.1  # Small rotation limits
constraint2.rigid_body_constraint.limit_ang_z_upper = 0.1

# 3. Fixed constraint between arm end and cube
bpy.ops.rigidbody.constraint_add()
constraint3 = bpy.context.active_object
constraint3.name = "Arm_Cube_Fixed"
constraint3.empty_display_type = 'ARROWS'
constraint3.location = cube_loc
constraint3.rigid_body_constraint.type = 'FIXED'
constraint3.rigid_body_constraint.object1 = arm
constraint3.rigid_body_constraint.object2 = cube

# Set collision margins for stability
for obj in [column, arm, cube]:
    if hasattr(obj, 'rigid_body'):
        obj.rigid_body.collision_margin = 0.04

# Ensure proper scene update
bpy.context.view_layer.update()