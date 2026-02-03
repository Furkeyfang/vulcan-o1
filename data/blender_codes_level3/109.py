import bpy
import math

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
mast_dim = (0.5, 0.5, 6.0)
mast_loc = (0.0, 0.0, 3.25)
hinge_loc = (0.0, 0.0, 6.25)
boom_dim = (6.0, 0.5, 0.5)
boom_loc = (0.0, 0.0, 3.25)
boom_rot_initial = (0.0, 0.0, math.radians(-90.0))  # Convert to radians
cw_radius = 0.5
cw_depth = 1.0
cw_loc_local = (0.0, 0.0, 0.5)
hook_radius = 0.2
hook_depth = 0.5
hook_loc_local = (0.0, 0.0, -5.75)
motor_target_velocity = 0.325

# Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "Base"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create Vertical Mast
bpy.ops.mesh.primitive_cube_add(size=1, location=mast_loc)
mast = bpy.context.active_object
mast.scale = mast_dim
mast.name = "Mast"
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'PASSIVE'

# Fixed constraint between Mast and Base
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
mast.select_set(True)
bpy.context.view_layer.objects.active = mast
bpy.ops.rigidbody.constraint_add()
constraint = bpy.context.active_object
constraint.name = "Mast_Base_Fixed"
constraint.rigid_body_constraint.type = 'FIXED'
constraint.location = (0, 0, mast_loc[2])  # Constraint at mast center

# Create Boom
bpy.ops.mesh.primitive_cube_add(size=1, location=boom_loc)
boom = bpy.context.active_object
boom.scale = boom_dim
boom.name = "Boom"
boom.rotation_euler = boom_rot_initial
bpy.ops.rigidbody.object_add()
boom.rigid_body.type = 'ACTIVE'

# Hinge constraint between Mast and Boom
bpy.ops.object.select_all(action='DESELECT')
mast.select_set(True)
boom.select_set(True)
bpy.context.view_layer.objects.active = boom
bpy.ops.rigidbody.constraint_add()
hinge = bpy.context.active_object
hinge.name = "Mast_Boom_Hinge"
hinge.rigid_body_constraint.type = 'HINGE'
hinge.location = hinge_loc
hinge.rigid_body_constraint.use_limit_ang_z = True
hinge.rigid_body_constraint.limit_ang_z_lower = math.radians(-90)  # Vertical down
hinge.rigid_body_constraint.limit_ang_z_upper = math.radians(0)    # Horizontal
hinge.rigid_body_constraint.use_motor_ang = True
hinge.rigid_body_constraint.motor_ang_target_velocity = motor_target_velocity
hinge.rigid_body_constraint.motor_ang_max_impulse = 100.0  # Sufficient torque

# Create Counterweight (cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=cw_radius, depth=cw_depth, 
                                    location=(0,0,0), rotation=(0, math.radians(90), 0))
counterweight = bpy.context.active_object
counterweight.name = "Counterweight"
# Parent to boom for initial placement, then unparent
counterweight.parent = boom
counterweight.matrix_parent_inverse = boom.matrix_world.inverted()
counterweight.location = cw_loc_local
counterweight.parent = None
bpy.ops.rigidbody.object_add()
counterweight.rigid_body.type = 'ACTIVE'

# Fixed constraint between Counterweight and Boom
bpy.ops.object.select_all(action='DESELECT')
boom.select_set(True)
counterweight.select_set(True)
bpy.context.view_layer.objects.active = counterweight
bpy.ops.rigidbody.constraint_add()
cw_constraint = bpy.context.active_object
cw_constraint.name = "Boom_Counterweight_Fixed"
cw_constraint.rigid_body_constraint.type = 'FIXED'
cw_constraint.location = hinge_loc  # Constraint at hinge point

# Create Hook (cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=hook_radius, depth=hook_depth,
                                    location=(0,0,0))
hook = bpy.context.active_object
hook.name = "Hook"
# Parent to boom for initial placement
hook.parent = boom
hook.matrix_parent_inverse = boom.matrix_world.inverted()
hook.location = hook_loc_local
hook.parent = None
bpy.ops.rigidbody.object_add()
hook.rigid_body.type = 'ACTIVE'

# Fixed constraint between Hook and Boom
bpy.ops.object.select_all(action='DESELECT')
boom.select_set(True)
hook.select_set(True)
bpy.context.view_layer.objects.active = hook
bpy.ops.rigidbody.constraint_add()
hook_constraint = bpy.context.active_object
hook_constraint.name = "Boom_Hook_Fixed"
hook_constraint.rigid_body_constraint.type = 'FIXED'
hook_constraint.location = hinge_loc

# Set rigid body world settings
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = 250

print("Crane assembly complete. Motor target velocity:", motor_target_velocity, "rad/s")