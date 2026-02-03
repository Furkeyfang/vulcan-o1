import bpy
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Extract parameters
total_height = 20.0
level_height = 1.0
level_width = 2.0
level_depth = 2.0
level_count = 20
offset_per_level = 0.5
load_mass = 300.0
load_size = 1.0
ground_size = 20.0
material_density = 800.0

# Calculate level mass
level_volume = level_width * level_depth * level_height
level_mass = level_volume * material_density

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create tower levels
levels = []
for i in range(level_count):
    x_pos = i * offset_per_level
    z_pos = i * level_height + level_height / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0.0, z_pos))
    level = bpy.context.active_object
    level.name = f"Level_{i}"
    level.scale = (level_width, level_depth, level_height)
    
    bpy.ops.rigidbody.object_add()
    if i == 0:
        level.rigid_body.type = 'PASSIVE'  # Base fixed to ground
    else:
        level.rigid_body.type = 'ACTIVE'
        level.rigid_body.mass = level_mass
        level.rigid_body.collision_shape = 'BOX'
    
    levels.append(level)

# Create fixed constraints between levels
for i in range(1, level_count):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=levels[i].location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = f"Constraint_{i-1}_{i}"
    
    bpy.ops.rigidbody.constraint_add()
    constraint = constraint_empty.rigid_body_constraint
    constraint.type = 'FIXED'
    
    # Link constraint to adjacent levels
    constraint.object1 = levels[i-1]
    constraint.object2 = levels[i]

# Create load cube
top_level = levels[-1]
load_x = top_level.location.x
load_z = total_height + load_size / 2

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(load_x, 0.0, load_z))
load = bpy.context.active_object
load.name = "Load"
load.scale = (load_size, load_size, load_size)

bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.mass = load_mass
load.rigid_body.collision_shape = 'BOX'

# Create constraint between top level and load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=((top_level.location.x + load_x)/2, 0.0, (top_level.location.z + load_z)/2))
load_constraint_empty = bpy.context.active_object
load_constraint_empty.name = "Load_Constraint"

bpy.ops.rigidbody.constraint_add()
load_constraint = load_constraint_empty.rigid_body_constraint
load_constraint.type = 'FIXED'
load_constraint.object1 = top_level
load_constraint.object2 = load

# Set up physics world
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.rigidbody_world.substeps_per_frame = 10
bpy.context.scene.rigidbody_world.solver_iterations = 50

print(f"Built stepped tower with {level_count} levels, total height {total_height}m")
print(f"Load mass: {load_mass}kg at position ({load_x}, 0.0, {load_z})")