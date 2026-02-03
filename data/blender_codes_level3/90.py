import bpy
import mathutils

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Extract variables from summary
base_dim = (2.0, 2.0, 0.3)
base_loc = (0.0, 0.0, 0.15)
turret_dim = (1.5, 1.5, 1.0)
turret_loc = (0.0, 0.0, 0.8)
hinge_pivot = (0.0, 0.0, 0.3)
motor_velocity = 1.0

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base_Platform"
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create Turret Body
bpy.ops.mesh.primitive_cube_add(size=1.0, location=turret_loc)
turret = bpy.context.active_object
turret.name = "Turret_Body"
turret.scale = turret_dim
bpy.ops.rigidbody.object_add()
turret.rigid_body.type = 'ACTIVE'
turret.rigid_body.collision_shape = 'BOX'

# Create Hinge Constraint (as empty object)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=hinge_pivot)
constraint = bpy.context.active_object
constraint.name = "Hinge_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint.rigid_body_constraint.type = 'HINGE'
constraint.rigid_body_constraint.object1 = turret
constraint.rigid_body_constraint.object2 = base
constraint.rigid_body_constraint.pivot_type = 'CUSTOM'
constraint.rigid_body_constraint.use_limit_ang_z = False
constraint.rigid_body_constraint.use_motor_ang_z = True
constraint.rigid_body_constraint.motor_ang_z_velocity = motor_velocity
constraint.rigid_body_constraint.motor_ang_z_max_impulse = 5.0

# Enable rigid body simulation in scene
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True

# Optional: Set simulation frames for verification
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100