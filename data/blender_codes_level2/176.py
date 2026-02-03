import bpy
import mathutils

# Clear existing scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Parameters from summary
col_w = 0.5
col_d = 0.5
col_h = 16.0
col_spacing = 4.0
plat_w = 5.0
plat_d = 5.0
plat_t = 0.5
load_mass = 2500.0
sim_frames = 100

col_positions = [(-2, -2, 8), (-2, 2, 8), (2, -2, 8), (2, 2, 8)]
plat_center = (0.0, 0.0, 16.25)
ground_size = 20.0

# Create Ground Plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'MESH'
ground.rigid_body.mass = 10000.0  # Very heavy ground

# Create Columns
columns = []
for i, pos in enumerate(col_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    col.scale = (col_w/2, col_d/2, col_h/2)  # Default cube is 2m, so /2 for correct dimensions
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'ACTIVE'
    col.rigid_body.mass = 100.0  # Estimated mass for 0.5x0.5x16m concrete column
    col.rigid_body.collision_shape = 'BOX'
    col.rigid_body.friction = 0.8
    col.rigid_body.restitution = 0.1
    columns.append(col)

# Create Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=plat_center)
platform = bpy.context.active_object
platform.name = "Platform"
platform.scale = (plat_w/2, plat_d/2, plat_t/2)
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = load_mass
platform.rigid_body.collision_shape = 'BOX'
platform.rigid_body.friction = 0.5
platform.rigid_body.restitution = 0.05

# Create Fixed Constraints: Column Bases to Ground
for col in columns:
    # Create constraint object at column base
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(col.location.x, col.location.y, 0))
    constraint = bpy.context.active_object
    constraint.name = f"Base_Constraint_{col.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = col
    constraint.rigid_body_constraint.object2 = ground

# Create Fixed Constraints: Column Tops to Platform
for col in columns:
    # Create constraint object at column top
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(col.location.x, col.location.y, 16))
    constraint = bpy.context.active_object
    constraint.name = f"Top_Constraint_{col.name}"
    bpy.ops.rigidbody.constraint_add()
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = col
    constraint.rigid_body_constraint.object2 = platform

# Set up rigid body world for stability
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.time_scale = 1.0

# Set simulation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = sim_frames

print(f"Structure created with {len(columns)} columns supporting {load_mass}kg platform.")
print(f"Simulation will run for {sim_frames} frames.")