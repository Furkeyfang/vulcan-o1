import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
mast_height = 8.0
mast_radius = 0.3
mast_loc = (0.0, 0.0, 4.5)
arm_length = 6.0
arm_cross_section = (0.4, 0.4)
arm_loc = (3.0, 0.0, 8.5)
hook_radius = 0.1
hook_height = 0.5
hook_loc = (6.0, 0.0, 8.25)
hook_mass = 500.0
counterweight_dim = (1.0, 1.0, 1.0)
counterweight_loc = (-6.0, 0.0, 7.5)
counterweight_mass = 500.0
arm_mass = 50.0
pivot_loc = (0.0, 0.0, 8.5)
hinge_axis = (0.0, 0.0, 1.0)
motor_velocity = 0.5

# Create Base
bpy.ops.mesh.primitive_cube_add(size=1, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'

# Create Mast
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=mast_radius, depth=mast_height, location=mast_loc)
mast = bpy.context.active_object
bpy.ops.rigidbody.object_add()
mast.rigid_body.type = 'PASSIVE'

# Create Arm
bpy.ops.mesh.primitive_cube_add(size=1, location=arm_loc)
arm = bpy.context.active_object
arm.scale = (arm_length, arm_cross_section[0], arm_cross_section[1])
bpy.ops.rigidbody.object_add()
arm.rigid_body.mass = arm_mass

# Create Load Hook
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=hook_radius, depth=hook_height, location=hook_loc)
hook = bpy.context.active_object
bpy.ops.rigidbody.object_add()
hook.rigid_body.mass = hook_mass

# Create Counterweight
bpy.ops.mesh.primitive_cube_add(size=1, location=counterweight_loc)
counterweight = bpy.context.active_object
counterweight.scale = counterweight_dim
bpy.ops.rigidbody.object_add()
counterweight.rigid_body.mass = counterweight_mass

# Set collision shapes for stability
for obj in [base, mast, arm, hook, counterweight]:
    obj.rigid_body.collision_shape = 'CONVEX_HULL'

# Function to add constraint between two objects
def add_constraint(obj_a, obj_b, const_type, pivot=obj_b.location, axis=hinge_axis):
    bpy.context.view_layer.objects.active = obj_a
    obj_b.select_set(True)
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.empty_display_type = 'ARROWS'
    constraint.rigid_body_constraint.type = const_type
    if const_type == 'HINGE':
        constraint.rigid_body_constraint.use_limit_ang_z = False
        constraint.rigid_body_constraint.use_motor_ang_z = True
        constraint.rigid_body_constraint.motor_ang_z_velocity = motor_velocity
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.location = pivot
    if const_type == 'HINGE':
        constraint.rigid_body_constraint.axis = axis

# Add constraints
add_constraint(base, mast, 'FIXED')
add_constraint(mast, arm, 'HINGE', pivot=pivot_loc)
add_constraint(arm, hook, 'FIXED')
add_constraint(mast, counterweight, 'FIXED')