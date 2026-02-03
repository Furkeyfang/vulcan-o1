import bpy
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# Parameters from summary
roof_size_x = 9.0
roof_size_y = 9.0
module_count_x = 3
module_count_y = 3
module_dim_x = 3.0
module_dim_y = 3.0
module_thickness = 0.3
base_z = 3.0
module_spacing_x = 3.0
module_spacing_y = 3.0
load_mass_kg = 1400.0
load_plate_thickness = 0.2
load_gap = 0.1
simulation_frames = 100
collision_margin = 0.04

# Calculate module positions
modules = []
for row in range(module_count_y):
    for col in range(module_count_x):
        pos_x = -roof_size_x/2 + (col + 0.5) * module_spacing_x
        pos_y = -roof_size_y/2 + (row + 0.5) * module_spacing_y
        pos_z = base_z + module_thickness/2
        
        # Create module cube
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pos_x, pos_y, pos_z))
        module = bpy.context.active_object
        module.scale = (module_dim_x/2, module_dim_y/2, module_thickness/2)
        module.name = f"Module_{row}_{col}"
        
        # Add rigid body (passive - fixed structure)
        bpy.ops.rigidbody.object_add()
        module.rigid_body.type = 'PASSIVE'
        module.rigid_body.collision_margin = collision_margin
        module.rigid_body.collision_shape = 'BOX'
        
        modules.append(module)

# Create fixed constraints between adjacent modules
for i, module in enumerate(modules):
    row = i // module_count_x
    col = i % module_count_x
    
    # Right neighbor
    if col < module_count_x - 1:
        right_neighbor = modules[i + 1]
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=module.location)
        constraint = bpy.context.active_object
        constraint.name = f"Constraint_R_{row}_{col}"
        bpy.ops.rigidbody.constraint_add()
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = module
        constraint.rigid_body_constraint.object2 = right_neighbor
    
    # Bottom neighbor
    if row < module_count_y - 1:
        bottom_neighbor = modules[i + module_count_x]
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=module.location)
        constraint = bpy.context.active_object
        constraint.name = f"Constraint_B_{row}_{col}"
        bpy.ops.rigidbody.constraint_add()
        constraint.rigid_body_constraint.type = 'FIXED'
        constraint.rigid_body_constraint.object1 = module
        constraint.rigid_body_constraint.object2 = bottom_neighbor

# Create load plate
load_pos_z = base_z + module_thickness + load_gap + load_plate_thickness/2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, load_pos_z))
load_plate = bpy.context.active_object
load_plate.scale = (roof_size_x/2, roof_size_y/2, load_plate_thickness/2)
load_plate.name = "Load_Plate"

# Add rigid body with mass
bpy.ops.rigidbody.object_add()
load_plate.rigid_body.type = 'ACTIVE'
load_plate.rigid_body.mass = load_mass_kg
load_plate.rigid_body.collision_margin = collision_margin
load_plate.rigid_body.collision_shape = 'BOX'
load_plate.rigid_body.use_margin = True

# Set up physics world
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 50
bpy.context.scene.rigidbody_world.use_split_impulse = True

# Set simulation frames
bpy.context.scene.frame_end = simulation_frames

# Optional: Bake simulation for verification (headless compatible)
# Note: Baking requires running simulation; we set up scene for simulation
print("Scene setup complete. Run simulation for", simulation_frames, "frames.")
print("Roof modules:", len(modules), "Fixed constraints created.")
print("Load mass:", load_mass_kg, "kg")