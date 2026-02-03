import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters from summary
scale_factor = 0.1
tower_height_total = 3.0
bottom_radius = 0.5
bottom_height = 1.2
bottom_loc_z = 0.6
middle_radius = 0.4
middle_height = 1.2
middle_loc_z = 1.8
top_radius = 0.3
top_height = 0.6
top_loc_z = 2.7
nacelle_size = 0.8
nacelle_loc_z = 3.4
nacelle_mass = 800.0
wind_force = 50.0
sim_frames = 100
material_density = 7850.0
ground_size = 10.0
constraint_breaking_threshold = 10000.0

# Enable rigid body physics
if bpy.context.scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create bottom cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=bottom_radius,
    depth=bottom_height,
    location=(0, 0, bottom_loc_z)
)
bottom = bpy.context.active_object
bottom.name = "Bottom_Cylinder"
bpy.ops.rigidbody.object_add()
bottom.rigid_body.type = 'ACTIVE'
bottom.rigid_body.mass = material_density * (math.pi * bottom_radius**2 * bottom_height)
bottom.rigid_body.collision_shape = 'CYLINDER'

# Create middle cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=middle_radius,
    depth=middle_height,
    location=(0, 0, middle_loc_z)
)
middle = bpy.context.active_object
middle.name = "Middle_Cylinder"
bpy.ops.rigidbody.object_add()
middle.rigid_body.type = 'ACTIVE'
middle.rigid_body.mass = material_density * (math.pi * middle_radius**2 * middle_height)
middle.rigid_body.collision_shape = 'CYLINDER'

# Create top cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=top_radius,
    depth=top_height,
    location=(0, 0, top_loc_z)
)
top = bpy.context.active_object
top.name = "Top_Cylinder"
bpy.ops.rigidbody.object_add()
top.rigid_body.type = 'ACTIVE'
top.rigid_body.mass = material_density * (math.pi * top_radius**2 * top_height)
top.rigid_body.collision_shape = 'CYLINDER'

# Create nacelle cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, nacelle_loc_z))
nacelle = bpy.context.active_object
nacelle.name = "Nacelle"
nacelle.scale = (nacelle_size, nacelle_size, nacelle_size)
bpy.ops.rigidbody.object_add()
nacelle.rigid_body.type = 'ACTIVE'
nacelle.rigid_body.mass = nacelle_mass

# Create fixed constraints
def add_fixed_constraint(obj_a, obj_b):
    bpy.ops.rigidbody.constraint_add()
    constraint = bpy.context.active_object
    constraint.empty_display_type = 'ARROWS'
    constraint.rigid_body_constraint.type = 'FIXED'
    constraint.rigid_body_constraint.object1 = obj_a
    constraint.rigid_body_constraint.object2 = obj_b
    constraint.rigid_body_constraint.breaking_threshold = constraint_breaking_threshold
    constraint.location = obj_b.location

# Constraint chain
add_fixed_constraint(ground, bottom)   # Ground to bottom
add_fixed_constraint(bottom, middle)   # Bottom to middle
add_fixed_constraint(middle, top)      # Middle to top
add_fixed_constraint(top, nacelle)     # Top to nacelle

# Apply wind force as constant force field (headless compatible)
bpy.ops.object.effector_add(type='FORCE', location=(0, 0, nacelle_loc_z))
wind = bpy.context.active_object
wind.name = "Wind_Force"
wind.field.type = 'FORCE'
wind.field.strength = wind_force
wind.field.direction = 'X'  # Horizontal along X-axis
wind.field.use_max_distance = True
wind.field.distance_max = 2.0  # Only affect nearby objects

# Set simulation frames
bpy.context.scene.frame_end = sim_frames

# Ensure proper collision margins
for obj in [bottom, middle, top, nacelle]:
    obj.rigid_body.collision_margin = 0.04

print("Wind turbine tower constructed with fixed constraints.")
print(f"Total height: {tower_height_total}m")
print(f"Nacelle mass: {nacelle_mass}kg")
print(f"Wind force: {wind_force}N applied for {sim_frames} frames")