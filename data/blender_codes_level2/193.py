import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters (extracted from summary)
base_size_xy = 2.0
layer_height = 1.0
num_layers = 18
tower_bottom_z = 0.0
platform_size_xy = 3.0
platform_thickness = 0.5
platform_center_z = 18.25
load_mass_kg = 2000.0
gravity = 9.81
load_force_N = load_mass_kg * gravity
simulation_frames = 100
force_ramp_frames = 10

# Enable Rigid Body World
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.enabled = True
bpy.context.scene.rigidbody_world.time_scale = 1.0
bpy.context.scene.frame_end = simulation_frames

# Create Tower Layers
layers = []
for i in range(num_layers):
    # Calculate center position
    z_center = tower_bottom_z + (i * layer_height) + (layer_height / 2.0)
    location = (0.0, 0.0, z_center)
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    cube = bpy.context.active_object
    cube.name = f"Tower_Layer_{i:02d}"
    cube.scale = (base_size_xy, base_size_xy, layer_height)
    
    # Add rigid body
    bpy.ops.rigidbody.object_add()
    if i == 0:
        cube.rigid_body.type = 'PASSIVE'  # Fixed base
    else:
        cube.rigid_body.type = 'ACTIVE'
        cube.rigid_body.mass = 100.0  # Arbitrary mass for stability
    
    layers.append(cube)

# Create Fixed Constraints between layers
for i in range(num_layers - 1):
    obj_a = layers[i]
    obj_b = layers[i + 1]
    
    # Create constraint empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj_b.location)
    empty = bpy.context.active_object
    empty.name = f"Fixed_Constraint_{i:02d}"
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = 'FIXED'
    constraint.object1 = obj_a
    constraint.object2 = obj_b

# Create Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, platform_center_z))
platform = bpy.context.active_object
platform.name = "Load_Platform"
platform.scale = (platform_size_xy, platform_size_xy, platform_thickness)

# Add rigid body to platform
bpy.ops.rigidbody.object_add()
platform.rigid_body.type = 'ACTIVE'
platform.rigid_body.mass = 500.0  # Platform mass separate from load

# Fixed Constraint: Top layer to platform
top_layer = layers[-1]
bpy.ops.object.empty_add(type='PLAIN_AXES', location=platform.location)
empty = bpy.context.active_object
empty.name = "Platform_Constraint"
bpy.ops.rigidbody.constraint_add()
constraint = empty.rigid_body_constraint
constraint.type = 'FIXED'
constraint.object1 = top_layer
constraint.object2 = platform

# Create Force Field for Load
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, platform_center_z))
force_empty = bpy.context.active_object
force_empty.name = "Load_Force_Field"
force_empty.empty_display_size = 1.0

# Add force field
bpy.ops.object.forcefield_add(type='FORCE')
force_field = force_empty.field
force_field.type = 'FORCE'
force_field.strength = 0.0  # Start at zero
force_field.direction = 'NEGATIVE_Z'
force_field.use_max_distance = True
force_field.distance_max = 0.5  # Only affect platform center region

# Animate force strength (ramp up over frames, then constant)
force_field.keyframe_insert(data_path="strength", frame=1)
force_field.strength = load_force_N
force_field.keyframe_insert(data_path="strength", frame=force_ramp_frames)
force_field.keyframe_insert(data_path="strength", frame=simulation_frames)

# Set platform as only affected object
force_empty.field.affected_objects.append(platform)

# Ensure proper collision margins (optional but good practice)
for obj in layers + [platform]:
    if obj.rigid_body:
        obj.rigid_body.collision_margin = 0.04

# Set gravity
bpy.context.scene.rigidbody_world.gravity = (0.0, 0.0, -gravity)