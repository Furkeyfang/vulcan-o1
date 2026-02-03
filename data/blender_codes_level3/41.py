import bpy
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
col_dim = (0.5, 0.5, 3.0)
col_loc = (0.0, 0.0, 2.25)
hinge_loc = (0.0, 0.0, 3.25)
arm_dim = (0.3, 3.0, 0.3)
arm_loc = (0.0, 1.5, 3.25)
holder_dim = (0.4, 0.4, 0.4)
holder_loc = (0.0, 3.0, 3.25)
proj_radius = 0.2
proj_loc = (0.0, 3.0, 3.25)
motor_velocity = 5.0

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.name = "Base"

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.scale = col_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.name = "Column"

# Fixed Constraint: Base → Column
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
column.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.rigidbody.connect_add(type='FIXED')

# Create Swinging Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'ACTIVE'
arm.name = "Arm"

# Hinge Constraint: Column → Arm (Y-axis rotation)
bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.connect_add(type='HINGE')
constraint = bpy.context.object.constraints["RigidBodyConstraint"]
constraint.object1 = column
constraint.object2 = arm
constraint.pivot_type = 'CENTER'
constraint.use_limit_ang_z = False  # Free rotation
constraint.use_motor_ang = True
constraint.motor_ang_target_velocity = motor_velocity
constraint.use_motor_ang = True  # Enable motor

# Adjust hinge pivot to specified location
constraint.pivot_x = hinge_loc[0]
constraint.pivot_y = hinge_loc[1]
constraint.pivot_z = hinge_loc[2]
constraint.axis_ang_x = 0.0
constraint.axis_ang_y = 1.0  # Y-axis rotation for XZ plane motion
constraint.axis_ang_z = 0.0

# Create Projectile Holder
bpy.ops.mesh.primitive_cube_add(size=1.0, location=holder_loc)
holder = bpy.context.active_object
holder.scale = holder_dim
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.name = "Holder"

# Fixed Constraint: Arm → Holder
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
holder.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.rigidbody.connect_add(type='FIXED')

# Create Projectile Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=proj_radius, location=proj_loc)
projectile = bpy.context.active_object
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.name = "Projectile"

# Configure physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Set initial frame
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100