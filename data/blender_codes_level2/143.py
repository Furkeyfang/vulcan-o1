import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Extract parameters from summary
platform_count = 5
platform_dim = (3.0, 3.0, 0.5)
platform_z_centers = [0.25, 3.25, 6.25, 9.25, 12.25]
column_count = 4
column_radius = 0.2
column_height = 12.5
column_base_z = -6.25
column_positions = [(-1.5, -1.5), (-1.5, 1.5), (1.5, -1.5), (1.5, 1.5)]
load_mass = 350
load_position = (0.0, 0.0, 12.25)
simulation_frames = 100

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()
bpy.context.scene.rigidbody_world.steps_per_second = 240  # Higher accuracy
bpy.context.scene.rigidbody_world.solver_iterations = 50

# Create columns (vertical supports)
columns = []
for i in range(column_count):
    x, y = column_positions[i]
    # Column center Z = base + height/2
    column_center_z = column_base_z + column_height / 2
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=column_radius,
        depth=column_height,
        location=(x, y, column_center_z)
    )
    col = bpy.context.active_object
    col.name = f"Column_{i+1}"
    
    # Rigid body physics (passive - static)
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    col.rigid_body.collision_shape = 'CYLINDER'
    col.rigid_body.mass = 100  # Approximate steel density
    
    columns.append(col)

# Create platforms (horizontal decks)
platforms = []
for i in range(platform_count):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, platform_z_centers[i]))
    plat = bpy.context.active_object
    plat.name = f"Platform_{i+1}"
    plat.scale = platform_dim
    
    # Rigid body physics (passive - static)
    bpy.ops.rigidbody.object_add()
    plat.rigid_body.type = 'PASSIVE'
    plat.rigid_body.collision_shape = 'BOX'
    plat.rigid_body.mass = 50  # Approximate concrete mass
    
    platforms.append(plat)

# Create fixed constraints between platforms and columns
constraint_counter = 0
for plat in platforms:
    plat_z = plat.location.z
    for col in columns:
        # Create constraint empty
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(col.location.x, col.location.y, plat_z))
        constraint = bpy.context.active_object
        constraint.name = f"Fixed_{constraint_counter}"
        constraint.empty_display_size = 0.3
        
        # Configure rigid body constraint
        bpy.ops.rigidbody.constraint_add()
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = plat
        constraint.rigid_body_constraint.object2 = col
        constraint.rigid_body_constraint.disable_collisions = True
        
        constraint_counter += 1

# Create load sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=load_position)
load = bpy.context.active_object
load.name = "Load_Sphere"

# Rigid body physics (active - dynamic)
bpy.ops.rigidbody.object_add()
load.rigid_body.type = 'ACTIVE'
load.rigid_body.collision_shape = 'SPHERE'
load.rigid_body.mass = load_mass
load.rigid_body.use_margin = True
load.rigid_body.collision_margin = 0.001

# Set simulation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = simulation_frames

# Optional: Bake simulation for verification
bpy.ops.ptcache.bake_all(bake=True)

print(f"Scaffold construction complete. {platform_count} platforms, {column_count} columns, {constraint_counter} fixed constraints.")
print(f"Load: {load_mass}kg sphere at {load_position}")