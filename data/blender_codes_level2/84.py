import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define parameters from summary
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
col_dim = (0.5, 0.5, 4.0)
col_loc = (0.0, 0.0, 2.5)
arm_dim = (6.0, 0.3, 0.3)
arm_loc = (3.0, 0.0, 4.5)
hook_radius = 0.2
hook_depth = 0.5
hook_loc = (6.0, 0.0, 4.5)
steel_density = 7850.0
load_mass = 700.0
simulation_frames = 100
gravity = -9.81

# Ensure rigid body world exists
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.gravity = (0, 0, gravity)

# Function to create rigid body with mass from volume
def create_rigid_body(obj, body_type='PASSIVE', density=steel_density):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = body_type
    if body_type == 'ACTIVE':
        obj.rigid_body.mass = density * (obj.dimensions.x * obj.dimensions.y * obj.dimensions.z)
    return obj

# 1. Create Base Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.name = "Base"
base.scale = (base_dim[0]/2, base_dim[1]/2, base_dim[2]/2)  # Scale from unit cube
create_rigid_body(base, 'PASSIVE')

# 2. Create Support Column
bpy.ops.mesh.primitive_cube_add(size=1.0, location=col_loc)
column = bpy.context.active_object
column.name = "Column"
column.scale = (col_dim[0]/2, col_dim[1]/2, col_dim[2]/2)
create_rigid_body(column, 'PASSIVE')

# 3. Create Horizontal Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=arm_loc)
arm = bpy.context.active_object
arm.name = "Arm"
arm.scale = (arm_dim[0]/2, arm_dim[1]/2, arm_dim[2]/2)
create_rigid_body(arm, 'PASSIVE')

# 4. Create Loading Hook (Cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=hook_radius,
    depth=hook_depth,
    location=hook_loc,
    rotation=(0, 0, 0)
)
hook = bpy.context.active_object
hook.name = "Hook"
create_rigid_body(hook, 'PASSIVE')

# 5. Create Fixed Constraints between components
def add_fixed_constraint(obj_a, obj_b):
    # Select target then active object
    bpy.context.view_layer.objects.active = obj_a
    obj_b.select_set(True)
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.name = f"Fixed_{obj_a.name}_{obj_b.name}"
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    obj_b.select_set(False)

# Apply constraints in assembly order
add_fixed_constraint(base, column)      # Base to Column
add_fixed_constraint(column, arm)       # Column to Arm
add_fixed_constraint(arm, hook)         # Arm to Hook

# 6. Create Test Load (700kg cube) attached to hook
load_size = 0.5
load_loc = (hook_loc[0], hook_loc[1], hook_loc[2] - hook_depth/2 - load_size/2)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size/2, load_size/2, load_size/2)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass

# Attach load to hook with fixed constraint
add_fixed_constraint(hook, load)

# 7. Configure simulation
bpy.context.scene.frame_end = simulation_frames
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

# 8. Bake simulation for verification
bpy.ops.ptcache.bake_all(bake=True)

print("Harbor loading arm construction complete. Simulation baked for", simulation_frames, "frames.")