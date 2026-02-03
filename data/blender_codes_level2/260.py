import bpy
import math

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Define variables from summary
roof_x_span = 12.0
roof_y_span = 18.0
roof_bottom_z = 3.0
roof_thickness = 1.0
cube_size = 0.2
x_grid = [0.0, 3.0, 6.0, 9.0, 12.0]
y_grid = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0]
z_layers = [3.0, 3.2, 3.4, 3.6, 3.8]
column_radius = 0.3
column_height = 3.0
column_locations = [(0,0,0), (12,0,0), (0,18,0), (12,18,0), (6,9,0), (12,9,0)]
total_mass = 3500.0
num_cubes = len(x_grid) * len(y_grid) * len(z_layers)
cube_mass = total_mass / num_cubes
ground_size = 50.0

# Function to add a fixed constraint between two objects
def add_fixed_constraint(obj1, obj2, name="Fixed_Constraint"):
    # Create an empty for the constraint
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=obj1.location)
    constraint_empty = bpy.context.active_object
    constraint_empty.name = name
    # Add rigid body constraint component
    bpy.ops.rigidbody.constraint_add()
    rb_constraint = constraint_empty.rigid_body_constraint
    rb_constraint.type = 'FIXED'
    rb_constraint.object1 = obj1
    rb_constraint.object2 = obj2

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=ground_size, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.rigidbody.object_add()
ground.rigid_body.type = 'PASSIVE'

# Create columns
columns = []
for i, (x, y, z) in enumerate(column_locations):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=column_radius,
        depth=column_height,
        location=(x, y, z + column_height/2)
    )
    col = bpy.context.active_object
    col.name = f"Column_{i}"
    bpy.ops.rigidbody.object_add()
    col.rigid_body.type = 'PASSIVE'
    columns.append(col)
    # Fix column to ground with a fixed constraint
    add_fixed_constraint(col, ground, name=f"Fix_Column_{i}_to_Ground")

# Create roof cubes and store them in a 3D dictionary
cube_dict = {}
for x in x_grid:
    for y in y_grid:
        for z in z_layers:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
            cube = bpy.context.active_object
            cube.scale = (cube_size, cube_size, cube_size)
            cube.name = f"Cube_X{x}_Y{y}_Z{z}"
            bpy.ops.rigidbody.object_add()
            cube.rigid_body.type = 'ACTIVE'
            cube.rigid_body.mass = cube_mass
            cube_dict[(x, y, z)] = cube

# Connect cubes with fixed constraints
# Avoid duplicates by connecting only to next in each direction
for x in x_grid:
    for y in y_grid:
        for z in z_layers:
            cube = cube_dict[(x, y, z)]
            # X neighbor
            if x + 3.0 in x_grid:
                neighbor = cube_dict.get((x + 3.0, y, z))
                if neighbor:
                    add_fixed_constraint(cube, neighbor, name=f"Fix_X_{x}_{y}_{z}")
            # Y neighbor
            if y + 3.0 in y_grid:
                neighbor = cube_dict.get((x, y + 3.0, z))
                if neighbor:
                    add_fixed_constraint(cube, neighbor, name=f"Fix_Y_{x}_{y}_{z}")
            # Z neighbor (next layer up)
            next_z = z + 0.2
            if next_z in z_layers:
                neighbor = cube_dict.get((x, y, next_z))
                if neighbor:
                    add_fixed_constraint(cube, neighbor, name=f"Fix_Z_{x}_{y}_{z}")

# Connect columns to nearest roof cubes (bottom layer at Z=3.0)
for col in columns:
    # Find the cube at the same (x,y) and Z=3.0
    x, y, _ = col.location
    # Column location is at its base; we need the top at (x, y, 3.0)
    # The bottom layer cubes are at Z=3.0
    cube = cube_dict.get((x, y, 3.0))
    if cube:
        add_fixed_constraint(col, cube, name=f"Fix_Column_{col.name}_to_Roof")
    else:
        # If not exact match, find the closest cube in the bottom layer
        min_dist = float('inf')
        closest_cube = None
        for grid_x in x_grid:
            for grid_y in y_grid:
                dist = math.hypot(grid_x - x, grid_y - y)
                if dist < min_dist:
                    min_dist = dist
                    closest_cube = cube_dict.get((grid_x, grid_y, 3.0))
        if closest_cube:
            add_fixed_constraint(col, closest_cube, name=f"Fix_Column_{col.name}_to_Roof_Approx")

# Set gravity to standard -9.81 m/s^2 (default in Blender)
bpy.context.scene.gravity = (0, 0, -9.81)

# Set simulation end frame
bpy.context.scene.frame_end = 100

# Optional: Set rigid body world settings for stability
bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容
bpy.context.scene.rigidbody_world.solver_iterations = 10

print(f"Created {len(cube_dict)} roof cubes and {len(columns)} columns.")
print(f"Each cube mass: {cube_mass} kg, total roof mass: {cube_mass * len(cube_dict)} kg")