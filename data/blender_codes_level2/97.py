import bpy
import math

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
ground_z = 0.0
column_dim = (0.3, 0.3, 2.0)
column_loc = (0.0, 0.0, 1.0)
arm_dim = (3.0, 0.2, 0.2)
arm_loc = (1.5, 0.0, 2.0)
hook_rod_radius = 0.05
hook_rod_depth = 0.5
hook_rod_loc = (3.0, 0.0, 1.75)
hook_shape_radius = 0.1
hook_shape_depth = 0.1
hook_shape_loc = (3.0, 0.0, 1.45)
hook_shape_rot = (0.0, math.pi/2, 0.0)  # 90° around Y
load_dim = (0.3, 0.3, 0.3)
load_loc = (3.0, 0.0, 1.2)
load_mass = 250.0
simulation_frames = 100

# Enable rigid body physics
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

# Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=column_loc)
column = bpy.context.active_object
column.name = "Support_Column"
column.scale = column_dim
bpy.ops.rigidbody.object_add()
column.rigid_body.type = 'PASSIVE'
column.rigid_body.collision_shape = 'BOX'

# Create Main Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Main_Arm"
arm.scale = arm_dim
bpy.ops.rigidbody.object_add()
arm.rigid_body.type = 'PASSIVE'
arm.rigid_body.collision_shape = 'BOX'

# Create Hook Rod (vertical cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=hook_rod_radius,
    depth=hook_rod_depth,
    location=hook_rod_loc
)
hook_rod = bpy.context.active_object
hook_rod.name = "Hook_Rod"
bpy.ops.rigidbody.object_add()
hook_rod.rigid_body.type = 'PASSIVE'
hook_rod.rigid_body.collision_shape = 'CYLINDER'

# Create Hook Shape (horizontal cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=hook_shape_radius,
    depth=hook_shape_depth,
    location=hook_shape_loc
)
hook_shape = bpy.context.active_object
hook_shape.name = "Hook_Shape"
hook_shape.rotation_euler = hook_shape_rot
bpy.ops.rigidbody.object_add()
hook_shape.rigid_body.type = 'PASSIVE'
hook_shape.rigid_body.collision_shape = 'CYLINDER'

# Create Load Cube
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = load_dim
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create Fixed Constraints
def create_fixed_constraint(obj1, obj2, name):
    """Create a fixed rigid body constraint between two objects"""
    const = bpy.data.objects.new(name, None)
    const.empty_display_type = 'ARROWS'
    bpy.context.collection.objects.link(const)
    const.rigid_body_constraint.type = 'FIXED'
    const.rigid_body_constraint.object1 = obj1
    const.rigid_body_constraint.object2 = obj2
    return const

# Column to Arm constraint
create_fixed_constraint(column, arm, "Col_Arm_Constraint")

# Arm to Hook Rod constraint
create_fixed_constraint(arm, hook_rod, "Arm_Rod_Constraint")

# Hook Rod to Hook Shape constraint
create_fixed_constraint(hook_rod, hook_shape, "Rod_Hook_Constraint")

# Hook Shape to Load constraint
create_fixed_constraint(hook_shape, load, "Hook_Load_Constraint")

# Set simulation parameters
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50

print("Crane assembly complete. Structure ready for 100-frame physics simulation.")