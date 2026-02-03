import bpy
import mathutils

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Parameters
base_dim = (3.0, 3.0, 0.5)
base_loc = (0.0, 0.0, 0.25)
col_dim = (0.5, 0.5, 10.5)
col_x_offset = 1.25
col_y_offset = 1.25
col_z_center = 5.75
top_dim = (2.0, 2.0, 0.5)
top_loc = (0.0, 0.0, 10.75)
load_mass = 4000.0
load_dim = (0.5, 0.5, 0.5)
load_loc = (0.0, 0.0, 11.25)  # On top surface (10.75 + 0.25 + 0.25)
sim_frames = 100

# Create base platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=base_loc)
base = bpy.context.active_object
base.scale = base_dim
base.name = "BasePlatform"
bpy.ops.rigidbody.object_add()
base.rigid_body.type = 'PASSIVE'
base.rigid_body.collision_shape = 'BOX'

# Create four columns
col_locations = [
    (col_x_offset, col_y_offset, col_z_center),
    (col_x_offset, -col_y_offset, col_z_center),
    (-col_x_offset, col_y_offset, col_z_center),
    (-col_x_offset, -col_y_offset, col_z_center)
]

columns = []
for i, loc in enumerate(col_locations):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    col = bpy.context.active_object
    col.scale = col_dim
    col.name = f"Column_{i+1}"
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    col.rigid_body.collision_shape = 'BOX'
    columns.append(col)

# Create top platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=top_loc)
top = bpy.context.active_object
top.scale = top_dim
top.name = "TopPlatform"
bpy.ops.rigidbody.object_add()
top.rigid_body.type = 'PASSIVE'
top.rigid_body.collision_shape = 'BOX'

# Create fixed constraints between base and columns
for col in columns:
    # Create constraint object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=col.location)
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{base.name}_{col.name}"
    constraint.empty_display_size = 0.5
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = base
    constraint.rigid_body_constraint.object2 = col

# Create fixed constraints between columns and top platform
for col in columns:
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(
        col.location.x,
        col.location.y,
        top_loc[2]
    ))
    constraint = bpy.context.active_object
    constraint.name = f"Fix_{col.name}_{top.name}"
    constraint.empty_display_size = 0.5
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = col
    constraint.rigid_body_constraint.object2 = top

# Create load (active rigid body)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=load_loc)
load = bpy.context.active_object
load.scale = load_dim
load.name = "Load_4000kg"
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Setup simulation parameters
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.frame_end = sim_frames

# Optional: Add ground plane for extra stability
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0,0,-0.1))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

print("Frame construction complete. Run simulation with bpy.ops.ptcache.bake_all()")