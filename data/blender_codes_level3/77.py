import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from parameter summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
column_dim = (0.5, 0.5, 4.0)
column_loc = (0.0, 0.0, 2.25)
boom_dim = (4.0, 0.5, 0.5)
boom_pivot_z = 4.25
boom_center_x = 2.0
holder_radius = 0.2
holder_depth = 0.5
holder_loc = (4.0, 0.0, 4.25)
projectile_radius = 0.15
projectile_loc = (4.0, 0.0, 4.25)
boom_motor_velocity = 2.0
holder_motor_velocity = 5.0

# Enable rigid body world
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True

# 1. Base Platform (Passive)
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# 2. Support Column (Passive, Fixed to Base)
bpy.ops.mesh.primitive_cube_add(size=1, location=column_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Fixed Constraint between Base and Column
bpy.ops.object.select_all(action='DESELECT')
column.select_set(True)
bpy.context.view_layer.objects.active = column
bpy.ops.rigidbody.constraint_add()
constraint_fixed = bpy.context.active_object
constraint_fixed.name = "Fixed_Base_Column"
constraint_fixed.rigid_body_constraint.type = 'FIXED'
constraint_fixed.rigid_body_constraint.object1 = base
constraint_fixed.rigid_body_constraint.object2 = column

# 3. Boom (Active, Hinged to Column)
bpy.ops.mesh.primitive_cube_add(size=1, location=(boom_center_x, 0, boom_pivot_z))
boom = bpy.context.active_object
boom.name = "Boom"
boom.scale = boom_dim
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'
boom.rigid_body.collision_shape = 'BOX'

# Hinge Constraint (Boom to Column) - Z-axis rotation
bpy.ops.object.select_all(action='DESELECT')
boom.select_set(True)
bpy.context.view_layer.objects.active = boom
bpy.ops.rigidbody.constraint_add()
constraint_boom = bpy.context.active_object
constraint_boom.name = "Hinge_Boom_Column"
constraint_boom.rigid_body_constraint.type = 'HINGE'
constraint_boom.rigid_body_constraint.object1 = column
constraint_boom.rigid_body_constraint.object2 = boom
constraint_boom.rigid_body_constraint.use_limit_z = False
constraint_boom.rigid_body_constraint.use_motor_z = True
constraint_boom.rigid_body_constraint.motor_angular_target_velocity = boom_motor_velocity
constraint_boom.rigid_body_constraint.motor_max_impulse = 10.0
# Set pivot at column top (0,0,boom_pivot_z) in world coordinates
constraint_boom.location = (0, 0, boom_pivot_z)

# 4. Projectile Holder (Active, Hinged to Boom)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=holder_radius, depth=holder_depth, location=holder_loc)
holder = bpy.context.active_object
holder.name = "Holder"
# Rotate cylinder to align with Y-axis for horizontal rotation
holder.rotation_euler = (0, 0, math.radians(90))
bpy.ops.rigidbody.object_add()
holder.rigid_body.type = 'ACTIVE'
holder.rigid_body.collision_shape = 'CYLINDER'

# Hinge Constraint (Holder to Boom) - Y-axis rotation
bpy.ops.object.select_all(action='DESELECT')
holder.select_set(True)
bpy.context.view_layer.objects.active = holder
bpy.ops.rigidbody.constraint_add()
constraint_holder = bpy.context.active_object
constraint_holder.name = "Hinge_Holder_Boom"
constraint_holder.rigid_body_constraint.type = 'HINGE'
constraint_holder.rigid_body_constraint.object1 = boom
constraint_holder.rigid_body_constraint.object2 = holder
constraint_holder.rigid_body_constraint.use_limit_y = False
constraint_holder.rigidbody_constraint.use_motor_y = True
constraint_holder.rigidbody_constraint.motor_angular_target_velocity = holder_motor_velocity
constraint_holder.rigidbody_constraint.motor_max_impulse = 10.0
# Set pivot at boom end (holder_loc)
constraint_holder.location = holder_loc

# 5. Projectile Sphere (Active)
bpy.ops.mesh.primitive_uv_sphere_add(radius=projectile_radius, location=projectile_loc)
projectile = bpy.context.active_object
projectile.name = "Projectile"
bpy.ops.rigidbody.object_add()
projectile.rigid_body.type = 'ACTIVE'
projectile.rigid_body.collision_shape = 'SPHERE'
projectile.rigid_body.mass = 0.5  # Lightweight for launch

# Verification Setup: Set end frame and gravity
bpy.context.scene.frame_end = 100
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print("Crane-launcher mechanism constructed. Motors activated.")
print(f"Boom hinge velocity: {boom_motor_velocity} rad/s")
print(f"Holder hinge velocity: {holder_motor_velocity} rad/s")